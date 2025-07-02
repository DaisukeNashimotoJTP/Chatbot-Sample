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
  onError?: (error: Event) => void;
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
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    try {
      // 認証トークンを追加
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const wsUrl = token 
        ? `${this.config.url}?token=${encodeURIComponent(token)}`
        : this.config.url;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.flushMessageQueue();
        this.config.onOpen?.();
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', event);
        this.isConnecting = false;
        this.config.onClose?.();
        
        // 再接続を試行
        if (this.reconnectAttempts < (this.config.maxReconnectAttempts || 5)) {
          setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`Reconnecting... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);
            this.connect();
          }, this.config.reconnectInterval);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.config.onError?.(error);
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
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // 接続されていない場合はキューに追加
      this.messageQueue.push(message);
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
    this.config.onMessage?.(message);

    // 型別のリスナーを実行
    const callbacks = this.listeners.get(message.type);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(message.data);
        } catch (error) {
          console.error('Error in WebSocket message callback:', error);
        }
      });
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
    const wsUrl = baseUrl.replace('http', 'ws') + '/ws';
    
    super({
      url: wsUrl,
      onOpen: () => {
        console.log('Chat WebSocket connected');
      },
      onClose: () => {
        console.log('Chat WebSocket disconnected');
      },
      onError: (error) => {
        console.error('Chat WebSocket error:', error);
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
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
