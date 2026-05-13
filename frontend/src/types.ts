export interface User {
  id: number;
  username: string;
  created_at: string;
}

export interface Channel {
  id: number;
  name: string;
  admin_id: number;
  created_at: string;
}

export interface Tag {
  id: number;
  name: string;
  channel_id: number;
}

export interface Message {
  id: number;
  channel_id: number;
  sender_id: number;
  sender_name: string | null;
  content: string;
  primary_tag_id: number | null;
  primary_tag_name: string | null;
  created_at: string;
}

export interface AnalyticsData {
  date: string;
  messages_count: number;
  active_users: number;
  subscribers_count: number;
}
