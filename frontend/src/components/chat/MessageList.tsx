'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  IconButton,
  Chip,
  CircularProgress,
  Container,
  Tooltip,
  Fade,
  Grow,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Reply as ReplyIcon,
  EmojiEmotions as EmojiIcon,
  ChatBubbleOutline as ChatBubbleIcon,
} from '@mui/icons-material';
import { useChannel } from '@/hooks/useChannel';
import { Message } from '@/types';
import { formatRelativeTime } from '@/utils/format';
import { getChatWebSocketClient } from '@/utils/websocket';
import { apiClient } from '@/lib/api';

interface MessageListProps {
  channelId: string;
}

const MessageList: React.FC<MessageListProps> = ({ channelId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const wsClient = getChatWebSocketClient();
  useEffect(() => {
    console.log('=== MessageList useEffect START ===');
    console.log('channelId:', channelId);
    console.log('Previous channelId (from cleanup):', channelId);

    if (!channelId) {
      console.log('No channelId provided, skipping message loading');
      return;
    }

    // チャンネルIDが変更されたときに前のメッセージをクリア
    console.log('Clearing previous messages and setting loading state');
    setMessages([]);
    setIsLoading(true);

    // 認証トークンを確認
    const token = localStorage.getItem('access_token');
    console.log(
      'Current auth token:',
      token ? token.substring(0, 50) + '...' : 'No token'
    );

    console.log('Calling loadMessages for channel:', channelId);
    loadMessages();

    // WebSocket接続とメッセージリスナー設定
    console.log('Connecting to WebSocket...');
    wsClient.connect();

    // WebSocket接続状態をログ出力
    const checkConnection = () => {
      console.log('WebSocket connection state:', wsClient.connectionState);
      console.log('WebSocket is connected:', wsClient.isConnected);
    };

    // 接続状態を定期的にチェック
    const interval = setInterval(checkConnection, 2000);

    // チャンネルに参加
    setTimeout(() => {
      console.log('Joining channel:', channelId);
      wsClient.joinChannel(channelId);
    }, 1000);

    const unsubscribeNewMessage = wsClient.subscribe('new_message', (data) => {
      console.log('Received new_message event:', data);
      if (data.channel_id === channelId) {
        // バックエンドのデータ構造に対応
        const message: Message = {
          id: data.id,
          channel_id: data.channel_id,
          user_id: data.user_id,
          content: data.content,
          message_type: data.message_type || 'text',
          reply_to: data.reply_to,
          reply_count: data.reply_count || 0,
          is_edited: data.is_edited || false,
          edited_at: data.edited_at,
          created_at: data.created_at,
          updated_at: data.updated_at,
          user_username: data.user_username,
          user_display_name: data.user_display_name,
          user_avatar_url: data.user_avatar_url,
        };
        console.log('Adding message to list:', message);
        setMessages((prev) => [...prev, message]);
        scrollToBottom();
      }
    });

    const unsubscribeMessageUpdate = wsClient.subscribe(
      'message_updated',
      (data) => {
        console.log('Received message_updated event:', data);
        if (data.channel_id === channelId) {
          const message = data.message || data;
          console.log('Updating message in list:', message);
          setMessages((prev) =>
            prev.map((msg) => (msg.id === message.id ? message : msg))
          );
        }
      }
    );

    const unsubscribeMessageDelete = wsClient.subscribe(
      'message_deleted',
      (data) => {
        console.log('Received message_deleted event:', data);
        if (data.channel_id === channelId) {
          console.log('Deleting message from list:', data.message_id);
          setMessages((prev) =>
            prev.filter((msg) => msg.id !== data.message_id)
          );
        }
      }
    );

    return () => {
      console.log('=== MessageList CLEANUP START ===');
      console.log('Cleaning up for channel:', channelId);
      clearInterval(interval);
      unsubscribeNewMessage();
      unsubscribeMessageUpdate();
      unsubscribeMessageDelete();
      console.log('=== MessageList CLEANUP END ===');
    };
  }, [channelId]);

  const loadMessages = async () => {
    setIsLoading(true);
    try {
      console.log('Loading messages for channel:', channelId);
      console.log('API client:', apiClient);

      const response = await apiClient.getMessages(channelId, { limit: 50 });
      console.log('API response status:', response.status);
      console.log('API response data:', response.data);

      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
        setHasMore(response.data.has_more || false);
        console.log('Loaded messages:', response.data.messages.length);
      } else {
        setMessages([]);
        setHasMore(false);
        console.log('No messages found or invalid response structure');
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
      }
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any;
        console.error('Error response:', axiosError.response?.data);
        console.error('Error status:', axiosError.response?.status);
      }
      setMessages([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleReaction = async (messageId: string, emoji: string) => {
    try {
      // リアクションの追加/削除をAPIで処理
      console.log('Reaction:', messageId, emoji);
    } catch (error) {
      console.error('Failed to add reaction:', error);
    }
  };

  const renderMessage = (message: Message, index: number) => {
    const prevMessage = index > 0 ? messages[index - 1] : null;
    const isSameUser = prevMessage?.user_id === message.user_id;
    const timeDiff = prevMessage
      ? new Date(message.created_at).getTime() -
        new Date(prevMessage.created_at).getTime()
      : Infinity;
    const isGrouped = isSameUser && timeDiff < 300000; // 5分以内

    return (
      <Grow in key={message.id} timeout={300}>
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            padding: isGrouped ? '0.25rem 1rem' : '0.5rem 1rem',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        >
          {/* ユーザーアバター */}
          <Box sx={{ minWidth: 40 }}>
            {!isGrouped && (
              <Avatar
                src={message.user_avatar_url || undefined}
                sx={{ width: 40, height: 40 }}
              >
                {(
                  message.user_display_name ||
                  message.user_username ||
                  ''
                ).charAt(0)}
              </Avatar>
            )}
          </Box>

          {/* メッセージ内容 */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            {!isGrouped && (
              <Box
                sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}
              >
                <Typography
                  variant="subtitle2"
                  fontWeight="bold"
                  color="text.primary"
                >
                  {message.user_display_name || message.user_username || ''}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatRelativeTime(message.created_at)}
                </Typography>
                {message.is_edited && (
                  <Chip
                    label="編集済み"
                    size="small"
                    variant="outlined"
                    sx={{ height: 16, fontSize: '0.6rem' }}
                  />
                )}
              </Box>
            )}

            <Typography
              variant="body1"
              sx={{
                wordBreak: 'break-word',
                whiteSpace: 'pre-wrap',
              }}
            >
              {message.content}
            </Typography>

            {/* リアクション */}
            {message.reaction_counts &&
              Object.keys(message.reaction_counts).length > 0 && (
                <Box
                  sx={{ display: 'flex', gap: 0.5, mt: 1, flexWrap: 'wrap' }}
                >
                  {Object.entries(message.reaction_counts).map(
                    ([emoji, count]) => (
                      <Chip
                        key={emoji}
                        label={`${emoji} ${count}`}
                        size="small"
                        variant={
                          message.user_reactions?.includes(emoji)
                            ? 'filled'
                            : 'outlined'
                        }
                        onClick={() => handleReaction(message.id, emoji)}
                        sx={{
                          height: 24,
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                        }}
                      />
                    )
                  )}
                </Box>
              )}

            {/* スレッド情報 */}
            {message.reply_count > 0 && (
              <Box sx={{ mt: 1 }}>
                <Chip
                  icon={<ChatBubbleIcon />}
                  label={`${message.reply_count}件のスレッド`}
                  size="small"
                  variant="outlined"
                  onClick={() => console.log('Open thread:', message.id)}
                  sx={{ cursor: 'pointer' }}
                />
              </Box>
            )}
          </Box>

          {/* アクションボタン */}
          <Box
            sx={{
              opacity: 0,
              transition: 'opacity 0.2s',
              display: 'flex',
              gap: 0.5,
              '&:hover': { opacity: 1 },
              '.message-item:hover &': { opacity: 1 },
            }}
            className="message-actions"
          >
            <Tooltip title="リアクション">
              <IconButton
                size="small"
                onClick={() => handleReaction(message.id, '👍')}
              >
                <EmojiIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="スレッドで返信">
              <IconButton size="small">
                <ReplyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="その他">
              <IconButton size="small">
                <MoreVertIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Grow>
    );
  };

  if (isLoading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        height: '100%',
        overflow: 'auto',
        padding: '1rem 0',
      }}
      className="message-list"
    >
      {messages.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '50%',
            gap: 2,
          }}
        >
          <Typography variant="h6" color="text.secondary">
            まだメッセージがありません
          </Typography>
          <Typography variant="body2" color="text.secondary">
            最初のメッセージを送信してみましょう！
          </Typography>
        </Box>
      ) : (
        <>
          {messages.map((message, index) => (
            <div key={message.id} className="message-item">
              {renderMessage(message, index)}
            </div>
          ))}
        </>
      )}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;
