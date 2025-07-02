'use client';

import React from 'react';
import {
  Toolbar,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Tag as TagIcon,
  Lock as LockIcon,
  Info as InfoIcon,
  Group as GroupIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
} from '@mui/icons-material';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useChannel } from '@/hooks/useChannel';
import { formatMemberCount } from '@/utils/format';

const Header: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const { currentChannel } = useChannel();

  if (!currentWorkspace) {
    return (
      <Toolbar>
        <Typography variant="h6" component="h1" fontWeight="medium">
          Chat System
        </Typography>
      </Toolbar>
    );
  }

  if (!currentChannel) {
    return (
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <Typography variant="h6" component="h1" fontWeight="medium">
            {currentWorkspace.name}
          </Typography>
          <Chip
            label={formatMemberCount(currentWorkspace.member_count || 0)}
            size="small"
            variant="outlined"
            icon={<GroupIcon />}
          />
        </Box>
      </Toolbar>
    );
  }

  return (
    <Toolbar>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        {/* チャンネル情報 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 0, flexGrow: 1 }}>
          {/* チャンネルアイコンと名前 */}
          <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
            {currentChannel.type === 'private' ? (
              <LockIcon sx={{ color: 'text.secondary', mr: 1 }} />
            ) : (
              <TagIcon sx={{ color: 'text.secondary', mr: 1 }} />
            )}
            <Typography variant="h6" component="h1" fontWeight="medium" noWrap>
              {currentChannel.name}
            </Typography>
          </Box>

          {/* お気に入りボタン */}
          <Tooltip title="お気に入りに追加">
            <IconButton size="small">
              <StarBorderIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          {/* チャンネル説明（デスクトップのみ） */}
          {currentChannel.description && (
            <Box
              sx={{
                display: { xs: 'none', md: 'flex' },
                alignItems: 'center',
                minWidth: 0,
                ml: 2,
              }}
            >
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  fontSize: '0.875rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  maxWidth: '300px',
                }}
              >
                {currentChannel.description}
              </Typography>
            </Box>
          )}
        </Box>

        {/* 右側の情報とアクション */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
          {/* メンバー数 */}
          {currentChannel.member_count && (
            <Chip
              label={formatMemberCount(currentChannel.member_count)}
              size="small"
              variant="outlined"
              icon={<GroupIcon />}
              sx={{ display: { xs: 'none', sm: 'flex' } }}
            />
          )}

          {/* チャンネル情報ボタン */}
          <Tooltip title="チャンネル情報">
            <IconButton size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* モバイル用のチャンネル説明 */}
      {currentChannel.description && (
        <Box
          sx={{
            display: { xs: 'block', md: 'none' },
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            px: 2,
            pb: 1,
            borderTop: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Typography variant="body2" color="text.secondary" noWrap>
            {currentChannel.description}
          </Typography>
        </Box>
      )}
    </Toolbar>
  );
};

export default Header;
