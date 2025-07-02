export interface Channel {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  type: 'public' | 'private';
  created_by: string;
  is_archived: boolean;
  member_count?: number;
  unread_count?: number;
  user_role?: string;
  last_message?: any;
  created_at: string;
  updated_at: string;
}

export interface ChannelCreate {
  name: string;
  description?: string;
  type: 'public' | 'private';
}

export interface ChannelUpdate {
  name?: string;
  description?: string;
}

export interface ChannelMember {
  user_id: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  role: string;
  joined_at: string;
  last_read_at?: string;
  notification_level: string;
}

export interface ChannelMembersList {
  members: ChannelMember[];
  total: number;
}

export interface ChannelInvite {
  user_ids: string[];
}