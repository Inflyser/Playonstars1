import { api } from './api';

export interface TopUser {
  rank: number;
  id: number;
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  stars_balance: number;
  photo_url: string;
}

export interface TopUsersResponse {
  users: TopUser[];
  total: number;
}

class TopService {
  async getTopUsers(limit: number = 100, offset: number = 0): Promise<TopUsersResponse> {
    const response = await api.get(`/api/top/users?limit=${limit}&offset=${offset}`);
    return response.data;
  }

  async getTopUser(telegramId: number): Promise<{ rank: number } | null> {
    try {
      const response = await api.get(`/api/top/user-rank/${telegramId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting user rank:', error);
      return null;
    }
  }
}

export const topService = new TopService();