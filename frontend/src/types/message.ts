export interface Message {
  id: string;
  channel_id: string;
  user_id: string;
  content?: string;
  message_type: 'text' | 'file' | 'system';
  reply_to?: string;
  thread_ts?: string;
  reply_count: number;
  is_edited: boolean;
  edited_at?: string;
  attachments?: any[];
  mentions?: string[];
  
  // User information
  user_username?: string;
  user_display_name?: string;
  user_avatar_url?: string;
  
  // Reaction information
  reaction_counts?: Record<string, number>;
  user_reactions?: string[];
  
  created_at: string;
  updated_at: string;
}

export interface MessageCreate {
  content: string;
  message_type?: 'text' | 'file' | 'system';
  reply_to?: string;
  attachments?: any[];
  mentions?: string[];
}

export interface MessageUpdate {
  content: string;
}

export interface MessageList {
  messages: Message[];
  total: number;
  has_more?: boolean;
}

export interface MessageReaction {
  id: string;
  message_id: string;
  user_id: string;
  emoji: string;
  created_at: string;
  
  // User information
  user_username: string;
  user_display_name: string;
  user_avatar_url?: string;
}

export interface MessageReactionCreate {
  emoji: string;
}

export interface ThreadResponse {
  parent_message: Message;
  replies: Message[];
  total_replies: number;
}