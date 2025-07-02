'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Container, Typography, CircularProgress, Avatar } from '@mui/material';
import { ChatBubble } from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard');
      } else {
        router.replace('/auth/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // ローディング表示
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
          <Avatar
            sx={{
              width: 80,
              height: 80,
              bgcolor: 'primary.main',
              mb: 3,
              mx: 'auto',
            }}
          >
            <ChatBubble sx={{ fontSize: 40 }} />
          </Avatar>
          <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
            Chat System
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mt: 3 }}>
            <CircularProgress size={24} />
            <Typography variant="body1" color="text.secondary">
              読み込み中...
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
