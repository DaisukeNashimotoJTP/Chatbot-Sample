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
import { formatRelativeTime, formatUserDisplayName } from '@/utils/format';
import { getChatWebSocketClient } from '@/utils/websocket';

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
    loadMessages();
    
    // WebSocket接続とメッセージリスナー設定
    wsClient.connect();
    
    const unsubscribeNewMessage = wsClient.subscribe('new_message', (data) => {
      if (data.channel_id === channelId) {
        setMessages(prev => [...prev, data.message]);
        scrollToBottom();
      }
    });

    const unsubscribeMessageUpdate = wsClient.subscribe('message_updated', (data) => {
      if (data.channel_id === channelId) {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === data.message.id ? data.message : msg
          )
        );
      }
    });

    const unsubscribeMessageDelete = wsClient.subscribe('message_deleted', (data) => {
      if (data.channel_id === channelId) {
        setMessages(prev => prev.filter(msg => msg.id !== data.message_id));
      }
    });

    return () => {
      unsubscribeNewMessage();
      unsubscribeMessageUpdate();
      unsubscribeMessageDelete();
    };
  }, [channelId]);

  const loadMessages = async () => {
    setIsLoading(true);
    try {
      // APIからメッセージを取得（実装は後で追加）
      // const response = await apiClient.getMessages(channelId);
      // setMessages(response.data.messages);
      
      // デモ用のダミーデータ
      const dummyMessages: Message[] = [
        {
          id: '1',
          channel_id: channelId,
          user_id: 'user1',
          content: 'こんにちは！新しいチャンネルですね。',
          message_type: 'text',
          reply_count: 0,
          is_edited: false,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date(Date.now() - 3600000).toISOString(),
          user: {
            id: 'user1',
            username: 'alice',
            display_name: 'Alice',
            avatar_url: undefined,
          },
          reactions: [
            {
              id: 'r1',
              message_id: '1',
              user_id: 'user2',
              emoji: '👍',
              created_at: new Date().toISOString(),
              user_username: 'bob',
              user_display_name: 'Bob',
              user_avatar_url: undefined,
            }
          ],
        },
        {
          id: '2',
          channel_id: channelId,
          user_id: 'user2',
          content: 'よろしくお願いします！プロジェクトについて話し合いましょう。',
          message_type: 'text',
          reply_count: 1,
          is_edited: false,
          created_at: new Date(Date.now() - 1800000).toISOString(),
          updated_at: new Date(Date.now() - 1800000).toISOString(),
          user: {
            id: 'user2',
            username: 'bob',
            display_name: 'Bob',
            avatar_url: undefined,
          },
          reactions: [],
        },
      ];
      
      setMessages(dummyMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
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
    const timeDiff = prevMessage ? 
      new Date(message.created_at).getTime() - new Date(prevMessage.created_at).getTime() : 
      Infinity;
    const isGrouped = isSameUser && timeDiff < 300000; // 5分以内

    return (
      <Grow in key={message.id} timeout={300}>
        <Box
          sx={{
            px: 3,
            py: isGrouped ? 0.5 : 2,
            '&:hover': {
              bgcolor: 'action.hover',
            },
            '&:hover .message-actions': {
              opacity: 1,
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
            {/* アバター */}
            <Box sx={{ width: 40, height: 40, flexShrink: 0 }}>
              {!isGrouped && (
                <Avatar
                  sx={{ 
                    width: 40, 
                    height: 40,
                    bgcolor: 'primary.main',
                    fontSize: '1rem',
                  }}
                  src={message.user?.avatar_url}
                >
                  {message.user?.display_name?.[0] || message.user?.username?.[0] || 'U'}
                </Avatar>
              )}
            </Box>

            {/* メッセージ内容 */}
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              {!isGrouped && (
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle2" fontWeight="medium">
                    {message.user ? formatUserDisplayName(message.user) : 'Unknown User'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatRelativeTime(message.created_at)}
                  </Typography>
                </Box>
              )}
              
              <Typography
                variant="body1"
                sx={{
                  wordBreak: 'break-word',
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.4,
                }}
              >
                {message.content}
                {message.is_edited && (
                  <Typography
                    component="span"
                    variant="caption"
                    color="text.secondary"
                    sx={{ ml: 1 }}
                  >
                    (編集済み)
                  </Typography>
                )}
              </Typography>

              {/* リアクション */}
              {message.reactions && message.reactions.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                  {Object.entries(
                    message.reactions.reduce((acc, reaction) => {
                      acc[reaction.emoji] = (acc[reaction.emoji] || 0) + 1;
                      return acc;
                    }, {} as Record<string, number>)
                  ).map(([emoji, count]) => (
                    <Chip
                      key={emoji}
                      label={`${emoji} ${count}`}
                      size="small"
                      variant="outlined"
                      onClick={() => handleReaction(message.id, emoji)}
                      sx={{
                        height: 24,
                        fontSize: '0.75rem',
                        bgcolor: 'primary.50',
                        borderColor: 'primary.200',
                        '&:hover': {
                          bgcolor: 'primary.100',
                        },
                      }}
                    />
                  ))}
                </Box>
              )}

              {/* スレッド返信 */}
              {message.reply_count > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Chip
                    icon={<ReplyIcon />}
                    label={`${message.reply_count}件の返信`}
                    size="small"
                    variant="outlined"
                    clickable
                    sx={{ fontSize: '0.75rem' }}
                  />
                </Box>
              )}
            </Box>

            {/* メッセージアクション */}
            <Box
              className="message-actions"
              sx={{
                opacity: 0,
                transition: 'opacity 0.2s',
                display: 'flex',
                gap: 0.5,
                flexShrink: 0,
              }}
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
        </Box>
      </Grow>
    );
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Container maxWidth="sm">
          <Box textAlign="center">
            <CircularProgress size={40} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              メッセージを読み込み中...
            </Typography>
          </Box>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        flexGrow: 1,
        overflow: 'auto',
        bgcolor: 'background.default',
      }}
    >
      {messages.length === 0 ? (
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Container maxWidth="sm">
            <Box textAlign="center">
              <ChatBubbleIcon
                sx={{
                  fontSize: 64,
                  color: 'text.secondary',
                  mb: 2,
                }}
              />
              <Typography variant="h5" gutterBottom fontWeight="medium">
                チャンネルの始まりです
              </Typography>
              <Typography variant="body1" color="text.secondary">
                最初のメッセージを送信してみましょう！
              </Typography>
            </Box>
          </Container>
        </Box>
      ) : (
        <Box sx={{ py: 2 }}>
          {messages.map((message, index) => renderMessage(message, index))}
          <div ref={messagesEndRef} />
        </Box>
      )}
    </Box>
  );
};

export default MessageList;
