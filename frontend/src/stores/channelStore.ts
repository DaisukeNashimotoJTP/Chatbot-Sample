import { create } from 'zustand';
import { Channel, ChannelCreate, ChannelUpdate } from '@/types/channel';
import { apiClient } from '@/lib/api';

interface ChannelState {
  channels: Channel[];
  currentChannel: Channel | null;
  isLoading: boolean;
  error: string | null;
}

interface ChannelActions {
  fetchChannels: (workspaceId: string, params?: any) => Promise<void>;
  createChannel: (workspaceId: string, data: ChannelCreate) => Promise<Channel>;
  getChannel: (channelId: string) => Promise<Channel>;
  updateChannel: (channelId: string, data: ChannelUpdate) => Promise<Channel>;
  deleteChannel: (channelId: string) => Promise<void>;
  joinChannel: (channelId: string) => Promise<Channel>;
  leaveChannel: (channelId: string) => Promise<void>;
  setCurrentChannel: (channel: Channel | null) => void;
  clearError: () => void;
}

type ChannelStore = ChannelState & ChannelActions;

export const useChannelStore = create<ChannelStore>((set, get) => ({
  // Initial state
  channels: [],
  currentChannel: null,
  isLoading: false,
  error: null,

  // Actions
  fetchChannels: async (workspaceId: string, params = {}) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.getChannels(workspaceId, params);
      const channels = response.data;

      set({
        channels,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to fetch channels',
      });
      throw error;
    }
  },

  createChannel: async (workspaceId: string, data: ChannelCreate) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.createChannel(workspaceId, data);
      const channel = response.data;

      set((state) => ({
        channels: [...state.channels, channel],
        isLoading: false,
      }));

      return channel;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to create channel',
      });
      throw error;
    }
  },

  getChannel: async (channelId: string) => {
    try {
      const response = await apiClient.getChannel(channelId);
      const channel = response.data;

      // Update channel in the list if it exists
      set((state) => ({
        channels: state.channels.map((c) =>
          c.id === channelId ? channel : c
        ),
        currentChannel: channel,
      }));

      return channel;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to get channel',
      });
      throw error;
    }
  },

  updateChannel: async (channelId: string, data: ChannelUpdate) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.updateChannel(channelId, data);
      const channel = response.data;

      set((state) => ({
        channels: state.channels.map((c) =>
          c.id === channelId ? channel : c
        ),
        currentChannel:
          state.currentChannel?.id === channelId
            ? channel
            : state.currentChannel,
        isLoading: false,
      }));

      return channel;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to update channel',
      });
      throw error;
    }
  },

  deleteChannel: async (channelId: string) => {
    try {
      set({ isLoading: true, error: null });

      await apiClient.deleteChannel(channelId);

      set((state) => ({
        channels: state.channels.filter((c) => c.id !== channelId),
        currentChannel:
          state.currentChannel?.id === channelId
            ? null
            : state.currentChannel,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to delete channel',
      });
      throw error;
    }
  },

  joinChannel: async (channelId: string) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.joinChannel(channelId);
      const channel = response.data;

      set((state) => ({
        channels: state.channels.some((c) => c.id === channelId)
          ? state.channels.map((c) => (c.id === channelId ? channel : c))
          : [...state.channels, channel],
        isLoading: false,
      }));

      return channel;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to join channel',
      });
      throw error;
    }
  },

  leaveChannel: async (channelId: string) => {
    try {
      set({ isLoading: true, error: null });

      await apiClient.leaveChannel(channelId);

      set((state) => ({
        channels: state.channels.filter((c) => c.id !== channelId),
        currentChannel:
          state.currentChannel?.id === channelId
            ? null
            : state.currentChannel,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to leave channel',
      });
      throw error;
    }
  },

  setCurrentChannel: (channel: Channel | null) => {
    set({ currentChannel: channel });
  },

  clearError: () => set({ error: null }),
}));