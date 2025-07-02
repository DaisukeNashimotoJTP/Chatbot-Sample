import { useChannelStore } from '@/stores/channelStore';

export const useChannel = () => {
  const {
    channels,
    currentChannel,
    isLoading,
    error,
    fetchChannels,
    createChannel,
    getChannel,
    updateChannel,
    deleteChannel,
    joinChannel,
    leaveChannel,
    setCurrentChannel,
    clearError,
  } = useChannelStore();

  return {
    channels,
    currentChannel,
    isLoading,
    error,
    fetchChannels,
    createChannel,
    getChannel,
    updateChannel,
    deleteChannel,
    joinChannel,
    leaveChannel,
    setCurrentChannel,
    clearError,
  };
};