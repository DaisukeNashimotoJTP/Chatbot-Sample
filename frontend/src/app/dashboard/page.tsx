'use client';

import { useEffect } from 'react';
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

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchWorkspaces();
    }
  }, [isAuthenticated, fetchWorkspaces]);

  useEffect(() => {
    if (currentWorkspace) {
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
          <MessageList channelId={currentChannel.id} />
          <MessageInput 
            channelId={currentChannel.id}
            placeholder={`#${currentChannel.name} にメッセージを送信`}
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
