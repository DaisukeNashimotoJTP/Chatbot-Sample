import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiError } from '@/types';

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.instance.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('access_token');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              // Create a separate axios instance for refresh to avoid interceptor loop
              const refreshResponse = await axios.post(
                `${this.instance.defaults.baseURL}/v1/auth/refresh`,
                { refresh_token: refreshToken },
                {
                  headers: {
                    'Content-Type': 'application/json',
                  },
                }
              );
              
              const { access_token, refresh_token } = refreshResponse.data;
              
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              
              return this.instance(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            if (typeof window !== 'undefined') {
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/auth/login';
            }
          }
        }

        // Transform error to our ApiError format
        const apiError: ApiError = {
          message: error.response?.data?.detail || error.message || 'An error occurred',
          status: error.response?.status,
          detail: error.response?.data?.message,
        };

        return Promise.reject(apiError);
      }
    );
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.instance.post('/v1/auth/login', {
      email,
      password,
    });
  }

  async register(data: {
    username: string;
    email: string;
    password: string;
    display_name: string;
  }) {
    return this.instance.post('/v1/auth/register', data);
  }

  async refreshToken(refreshToken: string) {
    return this.instance.post('/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
  }

  async logout() {
    return this.instance.post('/v1/auth/logout');
  }

  async getCurrentUser() {
    return this.instance.get('/v1/auth/me');
  }

  // Workspace endpoints
  async getWorkspaces() {
    return this.instance.get('/v1/workspaces');
  }

  async createWorkspace(data: any) {
    return this.instance.post('/v1/workspaces', data);
  }

  async getWorkspace(workspaceId: string) {
    return this.instance.get(`/v1/workspaces/${workspaceId}`);
  }

  async getWorkspaceBySlug(slug: string) {
    return this.instance.get(`/v1/workspaces/slug/${slug}`);
  }

  async updateWorkspace(workspaceId: string, data: any) {
    return this.instance.put(`/v1/workspaces/${workspaceId}`, data);
  }

  async deleteWorkspace(workspaceId: string) {
    return this.instance.delete(`/v1/workspaces/${workspaceId}`);
  }

  async joinWorkspace(inviteCode: string) {
    return this.instance.post('/v1/workspaces/join', {
      invite_code: inviteCode,
    });
  }

  async leaveWorkspace(workspaceId: string) {
    return this.instance.post(`/v1/workspaces/${workspaceId}/leave`);
  }

  async getWorkspaceMembers(workspaceId: string, params?: any) {
    return this.instance.get(`/v1/workspaces/${workspaceId}/members`, {
      params,
    });
  }

  // Channel endpoints
  async getChannels(workspaceId: string, params?: any) {
    return this.instance.get('/v1/channels', {
      params: { workspace_id: workspaceId, ...params },
    });
  }

  async createChannel(workspaceId: string, data: any) {
    return this.instance.post('/v1/channels', data, {
      params: { workspace_id: workspaceId },
    });
  }

  async getChannel(channelId: string) {
    return this.instance.get(`/v1/channels/${channelId}`);
  }

  async updateChannel(channelId: string, data: any) {
    return this.instance.put(`/v1/channels/${channelId}`, data);
  }

  async deleteChannel(channelId: string) {
    return this.instance.delete(`/v1/channels/${channelId}`);
  }

  async joinChannel(channelId: string) {
    return this.instance.post(`/v1/channels/${channelId}/join`);
  }

  async leaveChannel(channelId: string) {
    return this.instance.post(`/v1/channels/${channelId}/leave`);
  }

  async inviteToChannel(channelId: string, userIds: string[]) {
    return this.instance.post(`/v1/channels/${channelId}/invite`, {
      user_ids: userIds,
    });
  }

  async getChannelMembers(channelId: string, params?: any) {
    return this.instance.get(`/v1/channels/${channelId}/members`, {
      params,
    });
  }

  // Message endpoints
  async getMessages(channelId: string, params?: any) {
    return this.instance.get('/v1/messages', {
      params: { channel_id: channelId, ...params },
    });
  }

  async createMessage(channelId: string, data: any) {
    return this.instance.post('/v1/messages', data, {
      params: { channel_id: channelId },
    });
  }

  async getMessage(messageId: string) {
    return this.instance.get(`/v1/messages/${messageId}`);
  }

  async updateMessage(messageId: string, data: any) {
    return this.instance.put(`/v1/messages/${messageId}`, data);
  }

  async deleteMessage(messageId: string) {
    return this.instance.delete(`/v1/messages/${messageId}`);
  }

  async getThread(messageId: string, params?: any) {
    return this.instance.get(`/v1/messages/${messageId}/thread`, {
      params,
    });
  }

  async addReaction(messageId: string, emoji: string) {
    return this.instance.post(`/v1/messages/${messageId}/reactions`, {
      emoji,
    });
  }

  async removeReaction(messageId: string, emoji: string) {
    return this.instance.delete(`/v1/messages/${messageId}/reactions/${emoji}`);
  }

  async getReactions(messageId: string) {
    return this.instance.get(`/v1/messages/${messageId}/reactions`);
  }

  // User endpoints
  async getUsers(params?: any) {
    return this.instance.get('/v1/users', { params });
  }

  async getUser(userId: string) {
    return this.instance.get(`/v1/users/${userId}`);
  }

  async updateUser(userId: string, data: any) {
    return this.instance.put(`/v1/users/${userId}`, data);
  }
}

export const apiClient = new ApiClient();