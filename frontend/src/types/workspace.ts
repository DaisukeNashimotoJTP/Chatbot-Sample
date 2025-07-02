export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  avatar_url?: string;
  owner_id: string;
  is_public: boolean;
  invite_code?: string;
  max_members: number;
  member_count?: number;
  user_role?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceCreate {
  name: string;
  slug?: string;
  description?: string;
  avatar_url?: string;
  is_public?: boolean;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
  avatar_url?: string;
  is_public?: boolean;
}

export interface WorkspaceMember {
  user_id: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  role: string;
  joined_at: string;
  last_seen_at?: string;
}

export interface WorkspaceMembersList {
  members: WorkspaceMember[];
  total: number;
}

export interface WorkspaceInvite {
  invite_code: string;
}