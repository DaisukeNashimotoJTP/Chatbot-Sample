import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  LoginRequest, 
  RegisterRequest, 
  TokenRefreshRequest,
  User
} from '@/types/auth';
import {
  WorkspaceCreate,
  Workspace
} from '@/types/workspace';
import {
  ChannelCreate,
  Channel
} from '@/types/channel';
import {
  MessageCreate,
  MessageList,
  MessageReactionCreate
} from '@/types/message';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/v1';
    console.log('APIClient baseURL:', baseURL);
    
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // リクエストインターセプター
    this.client.interceptors.request.use((config) => {
      console.log('API Request:', config.method?.toUpperCase(), (config.baseURL || '') + (config.url || ''));
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // レスポンスインターセプター
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken({ refresh_token: refreshToken });
              const { access_token } = response.data;
              
              localStorage.setItem('access_token', access_token);
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // リフレッシュトークンも無効な場合はログアウト
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/auth/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // 認証API
  async login(data: LoginRequest): Promise<AxiosResponse<{ access_token: string; refresh_token: string; user: User }>> {
    return this.client.post('/auth/login', data);
  }

  async register(data: RegisterRequest): Promise<AxiosResponse<{ access_token: string; refresh_token: string; user: User }>> {
    return this.client.post('/auth/register', data);
  }

  async refreshToken(data: TokenRefreshRequest): Promise<AxiosResponse<{ access_token: string }>> {
    return this.client.post('/auth/refresh', data);
  }

  async logout(): Promise<AxiosResponse<void>> {
    return this.client.post('/auth/logout');
  }

  async getCurrentUser(): Promise<AxiosResponse<User>> {
    return this.client.get('/auth/me');
  }

  // ワークスペースAPI
  async getWorkspaces(): Promise<AxiosResponse<{ workspaces: Workspace[] }>> {
    return this.client.get('/workspaces');
  }

  async createWorkspace(data: WorkspaceCreate): Promise<AxiosResponse<Workspace>> {
    return this.client.post('/workspaces', data);
  }

  async getWorkspace(id: string): Promise<AxiosResponse<Workspace>> {
    return this.client.get(`/workspaces/${id}`);
  }

  // チャンネルAPI
  async getChannels(workspaceId: string): Promise<AxiosResponse<{ channels: Channel[] }>> {
    return this.client.get(`/workspaces/${workspaceId}/channels`);
  }

  async createChannel(workspaceId: string, data: ChannelCreate): Promise<AxiosResponse<Channel>> {
    return this.client.post(`/workspaces/${workspaceId}/channels`, data);
  }

  async getChannel(workspaceId: string, channelId: string): Promise<AxiosResponse<Channel>> {
    return this.client.get(`/workspaces/${workspaceId}/channels/${channelId}`);
  }

  // メッセージAPI
  async getMessages(channelId: string, limit?: number, before?: string): Promise<AxiosResponse<MessageList>> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (before) params.append('before', before);
    
    return this.client.get(`/channels/${channelId}/messages?${params.toString()}`);
  }

  async createMessage(channelId: string, data: MessageCreate): Promise<AxiosResponse<any>> {
    return this.client.post(`/channels/${channelId}/messages`, data);
  }

  async updateMessage(channelId: string, messageId: string, data: { content: string }): Promise<AxiosResponse<any>> {
    return this.client.put(`/channels/${channelId}/messages/${messageId}`, data);
  }

  async deleteMessage(channelId: string, messageId: string): Promise<AxiosResponse<void>> {
    return this.client.delete(`/channels/${channelId}/messages/${messageId}`);
  }

  // リアクションAPI
  async addReaction(messageId: string, data: MessageReactionCreate): Promise<AxiosResponse<any>> {
    return this.client.post(`/messages/${messageId}/reactions`, data);
  }

  async removeReaction(messageId: string, emoji: string): Promise<AxiosResponse<void>> {
    return this.client.delete(`/messages/${messageId}/reactions/${encodeURIComponent(emoji)}`);
  }

  // ファイルアップロードAPI
  async uploadFile(file: File, channelId?: string): Promise<AxiosResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);
    if (channelId) {
      formData.append('channel_id', channelId);
    }

    return this.client.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
}

// シングルトンインスタンス
const apiClient = new APIClient();

export default apiClient;
