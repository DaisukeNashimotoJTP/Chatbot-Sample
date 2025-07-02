'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';
import { RegisterForm } from '@/components/auth';

export default function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
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

  if (isAuthenticated) {
    return null; // リダイレクト中
  }

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <RegisterForm
        onSuccess={() => {
          router.push('/dashboard');
        }}
      />
    </Box>
  );
}
