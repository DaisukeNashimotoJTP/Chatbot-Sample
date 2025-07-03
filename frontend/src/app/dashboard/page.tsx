'use client';

import { useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useChannel } from '@/hooks/useChannel';
import { MainLayout } from '@/components/layout';
import { MessageList, MessageInput } from '@/components/chat';

export default function DashboardPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { currentWorkspace, fetchWorkspaces } = useWorkspace();
  const { currentChannel, fetchChannels } = useChannel();
  const router = useRouter();

  // メッセージ送信後のコールバック
  const handleMessageSent = useCallback((message: string) => {
    console.log('Message sent in dashboard:', message);
    // ここで追加の処理があれば実装
  }, []);

  // チャンネル変更をログに出力
  useEffect(() => {
    console.log('=== DASHBOARD: Current channel changed ===');
    console.log('currentChannel:', currentChannel);
    if (currentChannel) {
      console.log('Channel ID:', currentChannel.id);
      console.log('Channel Name:', currentChannel.name);
    }
  }, [currentChannel]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      console.log('User authenticated, fetching workspaces...');
      console.log(
        'Access token:',
        localStorage.getItem('access_token')?.substring(0, 50) + '...'
      );
      fetchWorkspaces();
    }
  }, [isAuthenticated, fetchWorkspaces]);

  useEffect(() => {
    if (currentWorkspace) {
      console.log('Current workspace:', currentWorkspace.id);
      fetchChannels(currentWorkspace.id);
    }
  }, [currentWorkspace, fetchChannels]);

  if (authLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <Container maxWidth="sm">
          <Box textAlign="center">
            <CircularProgress size={40} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              認証情報を確認中...
            </Typography>
          </Box>
        </Container>
      </Box>
    );
  }

  if (!isAuthenticated) {
    return null; // リダイレクト中
  }

  return (
    <MainLayout>
      {currentChannel ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <MessageList key={currentChannel.id} channelId={currentChannel.id} />
          <MessageInput
            channelId={currentChannel.id}
            placeholder={`#${currentChannel.name} にメッセージを送信`}
            onMessageSent={handleMessageSent}
          />
        </Box>
      ) : (
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <Container maxWidth="sm">
            <Box textAlign="center">
              <Typography variant="h4" gutterBottom fontWeight="medium">
                チャンネルを選択してください
              </Typography>
              <Typography variant="body1" color="text.secondary">
                左のサイドバーからチャンネルを選択するか、新しいチャンネルを作成してください。
              </Typography>
            </Box>
          </Container>
        </Box>
      )}
    </MainLayout>
  );
}
