/**
 * WebSocket関連のユーティリティ
 */

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event | Error) => void;
  onMessage?: (message: WebSocketMessage) => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private isConnecting = false;
  private messageQueue: WebSocketMessage[] = [];
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...config,
    };
  }

  connect(): void {
    if (
      this.isConnecting ||
      (this.ws && this.ws.readyState === WebSocket.OPEN)
    ) {
      console.log('WebSocket already connecting or connected');
      return;
    }

    this.isConnecting = true;

    try {
      // 認証トークンを追加
      const token =
        typeof window !== 'undefined'
          ? localStorage.getItem('access_token')
          : null;

      if (!token) {
        console.warn('No access token found for WebSocket connection');
        this.isConnecting = false;
        const error = new Error('No authentication token available');
        this.config.onError?.(error);
        return;
      }

      const wsUrl = `${this.config.url}?token=${encodeURIComponent(token)}`;
      console.log(
        'Attempting WebSocket connection to:',
        wsUrl.replace(/token=[^&]*/, 'token=[REDACTED]')
      );

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.flushMessageQueue();
        this.config.onOpen?.();
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
        });
        this.isConnecting = false;
        this.config.onClose?.();

        // 正常な切断（1000）やユーザーによる切断の場合は再接続しない
        if (event.code === 1000 || event.code === 1001) {
          console.log('WebSocket closed normally, not reconnecting');
          return;
        }

        // 再接続を試行
        if (this.reconnectAttempts < (this.config.maxReconnectAttempts || 5)) {
          setTimeout(() => {
            this.reconnectAttempts++;
            console.log(
              `Reconnecting... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`
            );
            this.connect();
          }, this.config.reconnectInterval);
        } else {
          console.error('Max reconnection attempts reached');
          const error = new Error('Failed to reconnect after maximum attempts');
          this.config.onError?.(error);
        }
      };

      this.ws.onerror = (error: Event) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;

        // エラーの詳細情報を提供
        const errorInfo = {
          type: error.type,
          target: error.target,
          timeStamp: error.timeStamp,
          readyState: this.ws?.readyState,
          url: this.config.url,
        };

        console.error('WebSocket error details:', errorInfo);

        // エラーコールバックを呼び出し
        if (this.config.onError) {
          this.config.onError(error);
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;

      // エラー情報を詳細にログ出力
      if (error instanceof Error) {
        console.error('WebSocket creation error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack,
        });
      }

      // エラーコールバックを呼び出し
      if (this.config.onError) {
        this.config.onError(
          error instanceof Error ? error : new Error(String(error))
        );
      }
    }
  }

  disconnect(): void {
    // 再接続試行を停止
    this.reconnectAttempts = this.config.maxReconnectAttempts || 5;

    if (this.ws) {
      // イベントリスナーをクリア
      this.ws.onopen = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;

      // 接続を閉じる
      if (
        this.ws.readyState === WebSocket.OPEN ||
        this.ws.readyState === WebSocket.CONNECTING
      ) {
        this.ws.close(1000, 'Client disconnect');
      }
      this.ws = null;
    }

    this.isConnecting = false;
    console.log('WebSocket disconnected manually');
  }

  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        const messageData = JSON.stringify(message);
        this.ws.send(messageData);
        console.log('WebSocket message sent:', message.type);
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        // エラーコールバックを呼び出し
        if (this.config.onError) {
          const errorObj =
            error instanceof Error ? error : new Error(String(error));
          this.config.onError(errorObj);
        }
      }
    } else {
      // 接続されていない場合はキューに追加
      this.messageQueue.push(message);
      console.log('WebSocket not connected, message queued:', message.type);

      // 接続を試行
      if (!this.isConnecting) {
        this.connect();
      }
    }
  }

  subscribe(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(callback);

    // アンサブスクライブ関数を返す
    return () => {
      const callbacks = this.listeners.get(type);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('WebSocket message received:', message);
    this.config.onMessage?.(message);

    // 型別のリスナーを実行
    const callbacks = this.listeners.get(message.type);
    if (callbacks) {
      console.log(
        `Executing ${callbacks.length} callbacks for message type: ${message.type}`
      );
      callbacks.forEach((callback) => {
        try {
          callback(message.data);
        } catch (error) {
          console.error('Error in WebSocket message callback:', error);
        }
      });
    } else {
      console.log(`No callbacks registered for message type: ${message.type}`);
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get connectionState(): string {
    if (!this.ws) return 'DISCONNECTED';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }
}

/**
 * チャットアプリケーション用のWebSocketクライアント
 */
export class ChatWebSocketClient extends WebSocketClient {
  constructor(baseUrl: string) {
    // baseUrlにAPIパス（/v1）が含まれている場合は除去
    const cleanBaseUrl = baseUrl.replace('/v1', '');
    const wsUrl = cleanBaseUrl.replace('http', 'ws') + '/v1/ws';

    console.log('ChatWebSocketClient URL:', wsUrl);

    super({
      url: wsUrl,
      onOpen: () => {
        console.log('Chat WebSocket connected');
      },
      onClose: () => {
        console.log('Chat WebSocket disconnected');
      },
      onError: (error: Event | Error) => {
        console.error('Chat WebSocket error:', error);

        // エラーの詳細情報をログ出力
        if (error instanceof Event) {
          console.error('WebSocket Event error:', {
            type: error.type,
            target: error.target,
            timeStamp: error.timeStamp,
          });
        } else if (error instanceof Error) {
          console.error('WebSocket Error object:', {
            name: error.name,
            message: error.message,
            stack: error.stack,
          });
        }
      },
    });
  }

  // チャンネルに参加
  joinChannel(channelId: string): void {
    this.send({
      type: 'join_channel',
      data: { channel_id: channelId },
    });
  }

  // チャンネルから退出
  leaveChannel(channelId: string): void {
    this.send({
      type: 'leave_channel',
      data: { channel_id: channelId },
    });
  }

  // メッセージを送信
  sendMessage(channelId: string, content: string, replyTo?: string): void {
    this.send({
      type: 'send_message',
      data: {
        channel_id: channelId,
        content,
        reply_to: replyTo,
      },
    });
  }

  // タイピング状態を送信
  sendTyping(channelId: string, isTyping: boolean): void {
    this.send({
      type: 'typing',
      data: {
        channel_id: channelId,
        is_typing: isTyping,
      },
    });
  }

  // オンライン状態を更新
  updatePresence(status: 'online' | 'away' | 'busy' | 'offline'): void {
    this.send({
      type: 'update_presence',
      data: { status },
    });
  }
}

/**
 * WebSocketクライアントのシングルトンインスタンス
 */
let chatWebSocketClient: ChatWebSocketClient | null = null;

export function getChatWebSocketClient(): ChatWebSocketClient {
  if (!chatWebSocketClient) {
    // 環境変数からWebSocket URLを取得
    let baseUrl = 'http://localhost:8000';

    if (typeof window !== 'undefined') {
      // ブラウザ環境では環境変数を直接使用
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;

      if (wsUrl) {
        // WebSocket URL が直接設定されている場合はそれを使用（http/httpsをws/wssに変換）
        const url = new URL(
          wsUrl.startsWith('ws') ? wsUrl : wsUrl.replace('http', 'ws')
        );
        baseUrl = `${url.protocol}//${url.host}`;
      } else if (apiUrl) {
        // API URL から WebSocket URL を推測
        baseUrl = apiUrl.replace('http', 'ws').replace('/v1', '');
      } else {
        // フォールバック: 現在のホストから推測
        baseUrl = window.location.origin
          .replace(':3000', ':8000')
          .replace('http', 'ws');
      }
    }

    console.log('Creating WebSocket client with base URL:', baseUrl);
    chatWebSocketClient = new ChatWebSocketClient(baseUrl);
  }
  return chatWebSocketClient;
}

export function disconnectChatWebSocket(): void {
  if (chatWebSocketClient) {
    chatWebSocketClient.disconnect();
    chatWebSocketClient = null;
  }
}
