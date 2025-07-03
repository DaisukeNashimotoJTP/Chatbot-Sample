'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  EmojiEmotions as EmojiIcon,
  AlternateEmail as MentionIcon,
} from '@mui/icons-material';
import { validateMessage } from '@/utils/validation';
import { getChatWebSocketClient } from '@/utils/websocket';

interface MessageInputProps {
  channelId: string;
  onMessageSent?: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({
  channelId,
  onMessageSent,
  placeholder = 'メッセージを入力...',
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');
  const textFieldRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const wsClient = getChatWebSocketClient();

  const sendTypingStatus = (typing: boolean) => {
    if (wsClient.isConnected) {
      wsClient.sendTyping(channelId, typing);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setMessage(value);
    setError('');

    // タイピング状態の管理
    if (value.trim() && !isTyping) {
      setIsTyping(true);
      sendTypingStatus(true);
    }

    // タイピング停止のタイマーをリセット
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      if (isTyping) {
        setIsTyping(false);
        sendTypingStatus(false);
      }
    }, 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || isSending || disabled) {
      return;
    }

    // バリデーション
    const validation = validateMessage(message);
    if (!validation.isValid) {
      setError(validation.error!);
      return;
    }

    setIsSending(true);
    setError('');

    try {
      console.log('Sending message:', message.trim(), 'to channel:', channelId);
      // WebSocket経由でメッセージを送信
      if (wsClient.isConnected) {
        console.log('WebSocket is connected, sending message...');
        wsClient.sendMessage(channelId, message.trim());
      } else {
        console.log('WebSocket not connected, attempting to connect...');
        wsClient.connect();
        // 接続後に送信
        setTimeout(() => {
          if (wsClient.isConnected) {
            console.log('WebSocket connected, sending queued message...');
            wsClient.sendMessage(channelId, message.trim());
          } else {
            console.error('WebSocket still not connected after retry');
          }
        }, 1000);
      }

      // タイピング状態をクリア
      if (isTyping) {
        setIsTyping(false);
        sendTypingStatus(false);
      }

      // 入力をクリア
      const sentMessage = message.trim();
      setMessage('');
      
      // メッセージ送信完了をコールバックで通知
      onMessageSent?.(sentMessage);

      // フォーカスを戻す
      textFieldRef.current?.focus();
      
      console.log('Message sent successfully:', sentMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
      setError('メッセージの送信に失敗しました');
    } finally {
      setIsSending(false);
    }
  };

  const handleFileUpload = () => {
    // ファイルアップロード機能（今後実装）
    console.log('File upload clicked');
  };

  const handleEmojiPicker = () => {
    // 絵文字ピッカー機能（今後実装）
    console.log('Emoji picker clicked');
  };

  const handleMentions = () => {
    // メンション機能（今後実装）
    console.log('Mentions clicked');
  };

  useEffect(() => {
    return () => {
      // コンポーネントのアンマウント時にタイピング状態をクリア
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      if (isTyping) {
        sendTypingStatus(false);
      }
    };
  }, [isTyping]);

  return (
    <Paper
      elevation={0}
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
        p: 2,
      }}
    >
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        {/* ファイルアップロードボタン */}
        <Tooltip title="ファイルを添付">
          <IconButton
            onClick={handleFileUpload}
            disabled={disabled}
            size="small"
            sx={{ mb: 0.5 }}
          >
            <AttachFileIcon />
          </IconButton>
        </Tooltip>

        {/* メッセージ入力フィールド */}
        <TextField
          ref={textFieldRef}
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder={placeholder}
          value={message}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          disabled={disabled || isSending}
          InputProps={{
            endAdornment: (
              <Box
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 1 }}
              >
                <Tooltip title="メンション">
                  <IconButton
                    size="small"
                    onClick={handleMentions}
                    disabled={disabled}
                  >
                    <MentionIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="絵文字">
                  <IconButton
                    size="small"
                    onClick={handleEmojiPicker}
                    disabled={disabled}
                  >
                    <EmojiIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
        />

        {/* 送信ボタン */}
        <Tooltip title="送信 (Enter)">
          <span>
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!message.trim() || isSending || disabled}
              size="large"
              sx={{
                mb: 0.5,
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '&:disabled': {
                  bgcolor: 'action.disabledBackground',
                  color: 'action.disabled',
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </span>
        </Tooltip>
      </Box>

      {/* ヒントテキスト */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ mt: 1, display: 'block' }}
      >
        <strong>Enter</strong> で送信、<strong>Shift + Enter</strong> で改行
      </Typography>
    </Paper>
  );
};

export default MessageInput;
