'use client';

import React from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  CircularProgress,
  Container,
} from '@mui/material';
import { useAuth } from '@/hooks/useAuth';
import { useWorkspace } from '@/hooks/useWorkspace';
import Sidebar from './Sidebar';
import Header from './Header';

const DRAWER_WIDTH = 280;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const { currentWorkspace } = useWorkspace();

  if (!isAuthenticated || !user) {
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

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* サイドバー */}
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            bgcolor: 'grey.50',
          },
        }}
      >
        <Sidebar />
      </Drawer>

      {/* メインコンテンツエリア */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* ヘッダー */}
        <AppBar
          position="static"
          elevation={0}
          sx={{
            bgcolor: 'background.paper',
            color: 'text.primary',
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Header />
        </AppBar>

        {/* コンテンツ */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: 'hidden',
            bgcolor: 'background.default',
          }}
        >
          {currentWorkspace ? (
            children
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
                  <Typography variant="h5" gutterBottom fontWeight="medium">
                    ワークスペースを選択してください
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    左のサイドバーからワークスペースを選択するか、
                    新しいワークスペースを作成してください。
                  </Typography>
                </Box>
              </Container>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
