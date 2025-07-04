'use client';

import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Divider,
  IconButton,
  Collapse,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Tag as TagIcon,
  Lock as LockIcon,
  ExpandLess,
  ExpandMore,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  WorkspacePremium as WorkspaceIcon,
} from '@mui/icons-material';
import { useAuth } from '@/hooks/useAuth';
import { useWorkspace } from '@/hooks/useWorkspace';
import { useChannel } from '@/hooks/useChannel';
import { formatUserDisplayName } from '@/utils/format';
import { validateWorkspaceName, validateChannelName } from '@/utils/validation';

const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const {
    workspaces,
    currentWorkspace,
    setCurrentWorkspace,
    createWorkspace,
    isLoading: workspaceLoading,
  } = useWorkspace();
  const {
    channels,
    currentChannel,
    setCurrentChannel,
    createChannel,
    isLoading: channelLoading,
  } = useChannel();

  const [showWorkspaceDialog, setShowWorkspaceDialog] = useState(false);
  const [showChannelDialog, setShowChannelDialog] = useState(false);
  const [workspaceName, setWorkspaceName] = useState('');
  const [channelName, setChannelName] = useState('');
  const [channelType, setChannelType] = useState<'public' | 'private'>(
    'public'
  );
  const [channelsExpanded, setChannelsExpanded] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleCreateWorkspace = async () => {
    const validation = validateWorkspaceName(workspaceName);
    if (!validation.isValid) {
      setErrors({ workspace: validation.error! });
      return;
    }

    try {
      await createWorkspace({
        name: workspaceName,
        description: `${workspaceName}のワークスペース`,
      });
      setShowWorkspaceDialog(false);
      setWorkspaceName('');
      setErrors({});
    } catch (error) {
      setErrors({ workspace: 'ワークスペースの作成に失敗しました' });
    }
  };

  const handleCreateChannel = async () => {
    if (!currentWorkspace) return;

    const validation = validateChannelName(channelName);
    if (!validation.isValid) {
      setErrors({ channel: validation.error! });
      return;
    }

    try {
      await createChannel(currentWorkspace.id, {
        name: channelName,
        type: channelType,
        description: `${channelName}チャンネル`,
      });
      setShowChannelDialog(false);
      setChannelName('');
      setChannelType('public');
      setErrors({});
    } catch (error) {
      setErrors({ channel: 'チャンネルの作成に失敗しました' });
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* ワークスペースヘッダー */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 1,
            }}
          >
            <Typography variant="h6" fontWeight="bold" noWrap>
              {currentWorkspace?.name || 'ワークスペースを選択'}
            </Typography>
            <IconButton size="small">
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Box>
          {user && (
            <Typography variant="body2" color="text.secondary" noWrap>
              {formatUserDisplayName(user)}
            </Typography>
          )}
        </Box>

        {/* ワークスペース一覧 */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 1,
            }}
          >
            <Typography variant="subtitle2" fontWeight="medium">
              ワークスペース
            </Typography>
            <IconButton
              size="small"
              onClick={() => setShowWorkspaceDialog(true)}
            >
              <AddIcon fontSize="small" />
            </IconButton>
          </Box>
          <List dense sx={{ py: 0 }}>
            {workspaces.map((workspace) => (
              <ListItem key={workspace.id} disablePadding>
                <ListItemButton
                  selected={currentWorkspace?.id === workspace.id}
                  onClick={() => setCurrentWorkspace(workspace)}
                  sx={{ borderRadius: 1, mb: 0.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <WorkspaceIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={workspace.name}
                    primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>

        {/* チャンネル一覧 */}

        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {currentWorkspace && (
            <Box sx={{ p: 2 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 1,
                }}
              >
                <Button
                  variant="text"
                  size="small"
                  startIcon={channelsExpanded ? <ExpandLess /> : <ExpandMore />}
                  onClick={() => setChannelsExpanded(!channelsExpanded)}
                  sx={{
                    color: 'text.secondary',
                    textTransform: 'none',
                    fontWeight: 'medium',
                    fontSize: '0.875rem',
                  }}
                >
                  チャンネル
                </Button>
                <IconButton
                  size="small"
                  onClick={() => setShowChannelDialog(true)}
                >
                  <AddIcon fontSize="small" />
                </IconButton>
              </Box>

              <Collapse in={channelsExpanded}>
                <List dense sx={{ py: 0 }}>
                  {channels.map((channel) => (
                    <ListItem key={channel.id} disablePadding>
                      <ListItemButton
                        selected={currentChannel?.id === channel.id}
                        onClick={() => setCurrentChannel(channel)}
                        sx={{ borderRadius: 1, mb: 0.5 }}
                      >
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          {channel.type === 'private' ? (
                            <LockIcon fontSize="small" />
                          ) : (
                            <TagIcon fontSize="small" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={channel.name}
                          primaryTypographyProps={{
                            variant: 'body2',
                            noWrap: true,
                          }}
                        />
                        {channel.unread_count && channel.unread_count > 0 && (
                          <Chip
                            label={
                              channel.unread_count > 99
                                ? '99+'
                                : channel.unread_count
                            }
                            size="small"
                            color="error"
                            sx={{ height: 20, fontSize: '0.75rem' }}
                          />
                        )}
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            </Box>
          )}
        </Box>

        {/* ユーザー情報とログアウト */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: 'primary.main',
                fontSize: '0.875rem',
              }}
            >
              {user?.display_name?.[0] || user?.username?.[0] || 'U'}
            </Avatar>
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography variant="body2" fontWeight="medium" noWrap>
                {formatUserDisplayName(user!)}
              </Typography>
              <Typography variant="caption" color="success.main">
                オンライン
              </Typography>
            </Box>
            <IconButton size="small" onClick={handleLogout} title="ログアウト">
              <LogoutIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* ワークスペース作成ダイアログ */}
      <Dialog
        open={showWorkspaceDialog}
        onClose={() => {
          setShowWorkspaceDialog(false);
          setWorkspaceName('');
          setErrors({});
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>新しいワークスペースを作成</DialogTitle>
        <DialogContent>
          {errors.workspace && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.workspace}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="ワークスペース名"
            fullWidth
            variant="outlined"
            value={workspaceName}
            onChange={(e) => setWorkspaceName(e.target.value)}
            placeholder="例: マイチーム"
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setShowWorkspaceDialog(false);
              setWorkspaceName('');
              setErrors({});
            }}
          >
            キャンセル
          </Button>
          <Button
            onClick={handleCreateWorkspace}
            variant="contained"
            disabled={workspaceLoading || !workspaceName.trim()}
          >
            作成
          </Button>
        </DialogActions>
      </Dialog>

      {/* チャンネル作成ダイアログ */}
      <Dialog
        open={showChannelDialog}
        onClose={() => {
          setShowChannelDialog(false);
          setChannelName('');
          setChannelType('public');
          setErrors({});
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>新しいチャンネルを作成</DialogTitle>
        <DialogContent>
          {errors.channel && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.channel}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="チャンネル名"
            fullWidth
            variant="outlined"
            value={channelName}
            onChange={(e) => setChannelName(e.target.value)}
            placeholder="例: general, random"
            helperText="小文字の英数字、ハイフン、アンダースコアのみ使用できます"
            sx={{ mb: 2 }}
          />
          <FormControl component="fieldset">
            <FormLabel component="legend">チャンネル種別</FormLabel>
            <RadioGroup
              value={channelType}
              onChange={(e) =>
                setChannelType(e.target.value as 'public' | 'private')
              }
            >
              <FormControlLabel
                value="public"
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TagIcon fontSize="small" />
                    公開チャンネル - 誰でも参加できます
                  </Box>
                }
              />
              <FormControlLabel
                value="private"
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LockIcon fontSize="small" />
                    プライベートチャンネル - 招待された人のみ参加できます
                  </Box>
                }
              />
            </RadioGroup>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setShowChannelDialog(false);
              setChannelName('');
              setChannelType('public');
              setErrors({});
            }}
          >
            キャンセル
          </Button>
          <Button
            onClick={handleCreateChannel}
            variant="contained"
            disabled={channelLoading || !channelName.trim()}
          >
            作成
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Sidebar;
