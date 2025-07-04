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
  const [currentTime, setCurrentTime] = useState(new Date());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const wsClient = getChatWebSocketClient();

  // メッセージキャッシュ
  const messageCache = useRef<{ [channelId: string]: Message[] }>({});

  // グループとメッセージの状態を一元管理
  const [messageStates, setMessageStates] = useState<{
    // キー: グループID（最初のメッセージID）、値: グループの時間表示
    groupTime: { [groupId: string]: string };
    // キー: メッセージID、値: 所属するグループID
    messageToGroup: { [messageId: string]: string };
    // キー: グループID、値: グループに属するメッセージIDの配列
    groupToMessages: { [groupId: string]: string[] };
  }>({
    groupTime: {},
    messageToGroup: {},
    groupToMessages: {},
  });

  // ヘルパー関数: メッセージが属するグループIDを取得
  const getMessageGroupId = (messageId: string): string => {
    return messageStates.messageToGroup[messageId] || messageId;
  };

  // ヘルパー関数: グループの時間表示を取得
  const getGroupTime = (groupId: string): string => {
    return messageStates.groupTime[groupId] || '今';
  };

  // ヘルパー関数: メッセージがグループ化されているかチェック
  const isMessageGrouped = (messageId: string, prevMessageId?: string): boolean => {
    if (!prevMessageId) return false;
    const currentGroupId = getMessageGroupId(messageId);
    const prevGroupId = getMessageGroupId(prevMessageId);
    return currentGroupId === prevGroupId && currentGroupId !== messageId;
  };

  // リアルタイム時間更新
  useEffect(() => {
    // 3秒ごとに現在時刻を更新し、時間表示とグループ化状態を再計算
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 3000);

    return () => clearInterval(interval);
  }, []);
  useEffect(() => {
    console.log('=== MessageList useEffect START ===');
    console.log('channelId:', channelId);
    console.log('Previous channelId (from cleanup):', channelId);

    if (!channelId) {
      console.log('No channelId provided, skipping message loading');
      return;
    }

    // チャンネルIDが変更されたときはキャッシュを確認してから処理
    console.log(
      'Channel changed, checking cache for chasetCurrentTimennel:',
      channelId
    );

    // キャッシュがあれば即座に表示
    if (messageCache.current[channelId]) {
      console.log('Using cached messages for channel:', channelId);
      setMessages(messageCache.current[channelId]);
      setIsLoading(false);
      setTimeout(scrollToBottom, 100);
    } else {
      console.log(
        'No cache found, clearing messages and setting loading state'
      );
      setMessages([]);
      setIsLoading(true);
    }

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
      // WebSocket接続状態のチェック（デバッグ時にコメントを解除）
      // console.log('WebSocket connection state:', wsClient.connectionState);
      // console.log('WebSocket is connected:', wsClient.isConnected);
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
        setMessages((prev) => {
          // 新しいメッセージを時系列順に挿入
          const newMessages = [...prev, message].sort(
            (a: Message, b: Message) =>
              new Date(a.created_at).getTime() -
              new Date(b.created_at).getTime()
          );
          // キャッシュも更新
          messageCache.current[channelId] = newMessages;

          // 新しいメッセージの時間状態とグループ化状態を設定
          setMessageStates((prevStates) => {
            console.log(
              '[新規メッセージ処理]',
              new Date().toLocaleTimeString()
            );

            const updatedGroupTime = { ...prevStates.groupTime };
            const updatedMessageToGroup = { ...prevStates.messageToGroup };
            const updatedGroupToMessages = { ...prevStates.groupToMessages };

            // 直前のメッセージを取得
            const lastMessage = newMessages[newMessages.length - 2];

            if (lastMessage) {
              // 基本条件: 同一ユーザーかつ1分以内のメッセージ
              const isSameUser = lastMessage.user_id === message.user_id;
              const timeDiff =
                new Date(message.created_at).getTime() -
                new Date(lastMessage.created_at).getTime();
              const isWithin1Min = timeDiff < 60000;

              // 直前メッセージのグループ情報を取得
              const lastMessageGroupId = prevStates.messageToGroup[lastMessage.id] || lastMessage.id;
              const lastMessageGroupTime = prevStates.groupTime[lastMessageGroupId] || '今';

              // グループ化条件: 同一ユーザーかつ1分以内かつ直前メッセージのグループが「今」
              if (isSameUser && isWithin1Min && lastMessageGroupTime === '今') {
                // グループ化実行 - 直前のグループに追加
                updatedMessageToGroup[message.id] = lastMessageGroupId;
                
                // グループのメッセージリストに追加
                if (!updatedGroupToMessages[lastMessageGroupId]) {
                  updatedGroupToMessages[lastMessageGroupId] = [lastMessage.id];
                }
                updatedGroupToMessages[lastMessageGroupId].push(message.id);
                
                console.log(
                  `[グループ化実行] メッセージID: ${message.id}, グループID: ${lastMessageGroupId}, 時間表示: ${lastMessageGroupTime}`
                );
              } else {
                // 新しいグループ作成
                const newGroupId = message.id; // 最初のメッセージIDがグループID
                updatedMessageToGroup[message.id] = newGroupId;
                updatedGroupToMessages[newGroupId] = [message.id];
                updatedGroupTime[newGroupId] = '今';
                
                console.log(
                  `[新しいグループ作成] メッセージID: ${message.id}, グループID: ${newGroupId}, 理由: ${
                    !isSameUser
                      ? '異なるユーザー'
                      : !isWithin1Min
                      ? '1分以上経過'
                      : `直前グループが「今」ではない (実際: "${lastMessageGroupTime}")`
                  }`
                );
                console.log(`[新しいグループ] グループID: ${newGroupId} の時間表示を「今」に設定 (常に新グループは「今」)`);
              }
            } else {
              // 最初のメッセージの場合は新しいグループを作成
              const newGroupId = message.id;
              updatedMessageToGroup[message.id] = newGroupId;
              updatedGroupToMessages[newGroupId] = [message.id];
              updatedGroupTime[newGroupId] = '今';
              console.log(`[最初のメッセージ] グループID: ${newGroupId} を「今」で作成 (最初のメッセージは常に「今」)`);
            }

            return {
              groupTime: updatedGroupTime,
              messageToGroup: updatedMessageToGroup,
              groupToMessages: updatedGroupToMessages,
            };
          });

          return newMessages;
        });
        // 新しいメッセージ追加時に現在時刻も更新
        setCurrentTime(new Date());
        // メッセージ送信後の自動スクロール
        setTimeout(scrollToBottom, 100);
      }
    });

    const unsubscribeMessageUpdate = wsClient.subscribe(
      'message_updated',
      (data) => {
        console.log('Received message_updated event:', data);
        if (data.channel_id === channelId) {
          const message = data.message || data;
          console.log('Updating message in list:', message);
          setMessages((prev) => {
            const updatedMessages = prev.map((msg) =>
              msg.id === message.id ? message : msg
            );
            // ソート順を維持
            const sortedMessages = updatedMessages.sort(
              (a: Message, b: Message) =>
                new Date(a.created_at).getTime() -
                new Date(b.created_at).getTime()
            );
            // キャッシュも更新
            messageCache.current[channelId] = sortedMessages;
            return sortedMessages;
          });
        }
      }
    );

    const unsubscribeMessageDelete = wsClient.subscribe(
      'message_deleted',
      (data) => {
        console.log('Received message_deleted event:', data);
        if (data.channel_id === channelId) {
          console.log('Deleting message from list:', data.message_id);
          setMessages((prev) => {
            const filteredMessages = prev.filter(
              (msg) => msg.id !== data.message_id
            );
            // キャッシュも更新
            messageCache.current[channelId] = filteredMessages;
            return filteredMessages;
          });
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
    console.log('=== loadMessages START ===');
    console.log('Channel ID for loading:', channelId);

    // キャッシュがない場合のみローディング状態を表示
    if (!messageCache.current[channelId]) {
      setIsLoading(true);
    }

    try {
      console.log('Making API call to getMessages...');
      const response = await apiClient.getMessages(channelId, { limit: 50 });
      console.log('=== API Response Details ===');
      console.log('Response status:', response.status);
      console.log('Response data structure:', {
        hasData: !!response.data,
        hasMessages: !!(response.data && response.data.messages),
        dataKeys: response.data ? Object.keys(response.data) : 'no data',
      });

      if (response.data && response.data.messages) {
        console.log('Processing messages...');
        console.log('Messages array length:', response.data.messages.length);

        // メッセージを送信時間で降順にソート（新しいメッセージが下）
        const sortedMessages = response.data.messages.sort(
          (a: Message, b: Message) =>
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );

        // メッセージをキャッシュに保存
        messageCache.current[channelId] = sortedMessages;

        setMessages(sortedMessages);

        // 初期のグループ状態を設定
        const initialGroupTime: { [groupId: string]: string } = {};
        const initialMessageToGroup: { [messageId: string]: string } = {};
        const initialGroupToMessages: { [groupId: string]: string[] } = {};

        // 最初のメッセージは必ず新しいグループとして「今」に設定
        if (sortedMessages.length > 0) {
          const firstMessage = sortedMessages[0];
          const firstGroupId = firstMessage.id;
          initialGroupTime[firstGroupId] = '今';
          initialMessageToGroup[firstMessage.id] = firstGroupId;
          initialGroupToMessages[firstGroupId] = [firstMessage.id];
          console.log(`[初期化] 最初のメッセージ ${firstMessage.id} のグループ ${firstGroupId} を「今」に設定 (最初のグループは常に「今」)`);
        }

        // 残りのメッセージのグループ化を処理
        for (let i = 1; i < sortedMessages.length; i++) {
          const message = sortedMessages[i];
          const prevMessage = sortedMessages[i - 1];

          // 基本グループ化条件: 同一ユーザーで1分以内のメッセージ
          const isSameUser = prevMessage.user_id === message.user_id;
          const timeDiff =
            new Date(message.created_at).getTime() -
            new Date(prevMessage.created_at).getTime();
          const isWithin1Min = timeDiff < 60000;

          // 直前メッセージのグループ情報を取得
          const prevGroupId = initialMessageToGroup[prevMessage.id];
          const prevGroupTime = initialGroupTime[prevGroupId];

          // グループ化条件: 同一ユーザーかつ1分以内かつ直前グループが「今」
          if (isSameUser && isWithin1Min && prevGroupTime === '今') {
            // グループ化実行 - 直前のグループに追加
            initialMessageToGroup[message.id] = prevGroupId;
            initialGroupToMessages[prevGroupId].push(message.id);
            console.log(`[初期化] グループ化: ${message.id} -> グループ ${prevGroupId} (直前が「今」)`);
          } else {
            // 新しいグループの作成 - 必ず時間表示を「今」に設定
            const newGroupId = message.id;
            initialGroupTime[newGroupId] = '今'; // 新しいグループは常に「今」
            initialMessageToGroup[message.id] = newGroupId;
            initialGroupToMessages[newGroupId] = [message.id];
            console.log(`[初期化] 新しいグループ作成: ${message.id} -> グループ ${newGroupId} (時間: 今 - 新グループは常に「今」)`);
          }
        }

        console.log('[初期化] グループ時間状態:', initialGroupTime);
        console.log('[初期化] メッセージ→グループ:', initialMessageToGroup);
        console.log('[初期化] グループ→メッセージ:', initialGroupToMessages);

        // 一元管理の状態に設定
        setMessageStates({
          groupTime: initialGroupTime,
          messageToGroup: initialMessageToGroup,
          groupToMessages: initialGroupToMessages,
        });

        setHasMore(response.data.has_more || false);
        console.log(
          '✓ Messages set successfully:',
          sortedMessages.length,
          'messages'
        );
      } else {
        console.log('⚠ No messages in response or invalid structure');
        setMessages([]);
        setHasMore(false);
      }
    } catch (error) {
      console.error('=== loadMessages ERROR ===');
      console.error('Error object:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any;
        console.error('HTTP Status:', axiosError.response?.status);
        console.error('Response data:', axiosError.response?.data);
      }
      setMessages([]);
      setHasMore(false);
    } finally {
      console.log('Setting isLoading to false');
      setIsLoading(false);
      // 確実にスクロールを実行
      setTimeout(() => {
        console.log('Calling scrollToBottom');
        scrollToBottom();
      }, 200);
    }
    console.log('=== loadMessages END ===');
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
        inline: 'nearest',
      });
    }
    // フォールバック: コンテナの直接スクロール
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  };

  // 新しいメッセージが追加されたときに自動スクロール
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(scrollToBottom, 100);
    }
  }, [messages.length]);

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

    // グループ化状態を確認 - 新しいヘルパー関数を使用
    const isGrouped = isMessageGrouped(message.id, prevMessage?.id);

    // 時間表示をグループから取得
    const groupId = getMessageGroupId(message.id);
    const displayTime = getGroupTime(groupId);

    // デバッグログ: レンダリング時の状態を確認
    console.log(`[レンダリング] メッセージID: ${message.id}, グループID: ${groupId}, グループ化: ${isGrouped}, 時間表示: "${displayTime}" ${isGrouped ? '(グループ内)' : '(グループ先頭)'}`);

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
                  {displayTime}
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

  // グループの時間表示のみを動的に更新
  useEffect(() => {
    if (messages.length === 0) return;

    setMessageStates((prevStates) => {
      const updatedGroupTime = { ...prevStates.groupTime };
      let hasChanges = false;

      console.log(`[時間更新] 開始 - ${Object.keys(prevStates.groupTime).length}個のグループを確認`);

      // 各グループの時間表示を更新
      for (const groupId of Object.keys(prevStates.groupTime)) {
        const groupMessages = prevStates.groupToMessages[groupId] || [];
        if (groupMessages.length === 0) continue;

        // グループの最初のメッセージの作成時間を基準にする
        const firstMessageId = groupMessages[0];
        const firstMessage = messages.find(m => m.id === firstMessageId);
        
        if (firstMessage) {
          const oldTime = updatedGroupTime[groupId];
          const newTime = formatRelativeTime(firstMessage.created_at, currentTime);
          
          // 時間表示の更新（変更があった場合のみ）
          if (oldTime !== newTime) {
            updatedGroupTime[groupId] = newTime;
            hasChanges = true;
            console.log(`[時間更新] グループID: ${groupId}, ${oldTime} -> ${newTime} (${groupMessages.length}件のメッセージが更新: ${groupMessages.join(', ')})`);
          }
        }
      }

      console.log(`[時間更新] 完了 - 変更あり: ${hasChanges}`);

      // 変更があった場合のみ状態を更新
      return hasChanges
        ? {
            groupTime: updatedGroupTime,
            messageToGroup: prevStates.messageToGroup, // メッセージ→グループのマッピングは変更しない
            groupToMessages: prevStates.groupToMessages, // グループ→メッセージのマッピングは変更しない
          }
        : prevStates;
    });
  }, [currentTime, messages]);

  if (isLoading && messages.length === 0) {
    console.log('MessageList rendering: LOADING state');
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '200px',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <CircularProgress size={32} />
        <Typography variant="body2" color="text.secondary">
          メッセージを読み込み中...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        height: '100%',
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: '1rem 0',
        display: 'flex',
        flexDirection: 'column',
        scrollBehavior: 'smooth',
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
      {/* スクロール位置のアンカー */}
      <div
        ref={messagesEndRef}
        style={{
          height: '1px',
          visibility: 'hidden',
          flexShrink: 0,
        }}
      />
    </Box>
  );
};

export default MessageList;
