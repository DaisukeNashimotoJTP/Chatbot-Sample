/**
 * WebSocket utils のテスト
 */
import {
  WebSocketClient,
  ChatWebSocketClient,
  getChatWebSocketClient,
} from '../websocket';

// WebSocketのモック
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // 非同期で接続状態をシミュレート
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }

  send(data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      const closeEvent = new CloseEvent('close', {
        code: code || 1000,
        reason: reason || '',
        wasClean: true,
      });
      this.onclose(closeEvent);
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
}

// グローバルWebSocketをモック
(globalThis as any).WebSocket = MockWebSocket;

describe('WebSocketClient', () => {
  let wsClient: WebSocketClient;
  let mockOnOpen: jest.Mock;
  let mockOnClose: jest.Mock;
  let mockOnError: jest.Mock;

  beforeEach(() => {
    mockOnOpen = jest.fn();
    mockOnClose = jest.fn();
    mockOnError = jest.fn();

    // localStorage のモック
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: () => 'mock-token',
      },
      writable: true,
    });

    wsClient = new WebSocketClient({
      url: 'ws://localhost:8000/ws',
      onOpen: mockOnOpen,
      onClose: mockOnClose,
      onError: mockOnError,
    });
  });

  afterEach(() => {
    if (wsClient) {
      wsClient.disconnect();
    }
  });

  test('should connect successfully', async () => {
    wsClient.connect();

    // 接続完了を待つ
    await new Promise((resolve) => setTimeout(resolve, 20));

    expect(wsClient.isConnected).toBe(true);
    expect(mockOnOpen).toHaveBeenCalled();
  });

  test('should handle connection errors', async () => {
    wsClient.connect();

    // 接続完了を待つ
    await new Promise((resolve) => setTimeout(resolve, 20));

    // エラーをシミュレート
    (wsClient as any).ws.simulateError();

    expect(mockOnError).toHaveBeenCalled();
  });

  test('should send messages when connected', async () => {
    wsClient.connect();
    await new Promise((resolve) => setTimeout(resolve, 20));

    const message = { type: 'test', data: { content: 'Hello' } };

    expect(() => wsClient.send(message)).not.toThrow();
  });
});

describe('ChatWebSocketClient', () => {
  test('should create chat WebSocket client', () => {
    const chatClient = new ChatWebSocketClient('http://localhost:8000');
    expect(chatClient).toBeInstanceOf(ChatWebSocketClient);
    expect(chatClient).toBeInstanceOf(WebSocketClient);
  });
});

describe('getChatWebSocketClient singleton', () => {
  test('should return same instance', () => {
    const client1 = getChatWebSocketClient();
    const client2 = getChatWebSocketClient();

    expect(client1).toBe(client2);
  });
});
