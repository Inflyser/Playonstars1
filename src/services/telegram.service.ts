import { api } from './api';

export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  photo_url?: string;
}

export interface UserBalance {
  ton_balance: number;
  stars_balance: number;
}

export interface AuthResponse {
  status: string;
  user: {
    id: number;
    telegram_id: number;
    username?: string;
    first_name?: string;
    last_name?: string;
    ton_balance: number;
    stars_balance: number;
  };
}

class TelegramService {
  async authTelegram(initData: string): Promise<AuthResponse> {
    const response = await api.post('/api/auth/telegram', { initData });
    return response.data;
  }

  async getUserData(): Promise<{ user_data: TelegramUser }> {
    const response = await api.get('/api/user/data');
    return response.data;
  }

  async getBalance(): Promise<UserBalance> {
    const response = await api.get('/api/user/balance');
    return response.data;
  }

  async getUserLanguage(): Promise<{ language: string }> {
    const response = await api.get('/api/user/language');
    return response.data;
  }

  async makeDeposit(amount: number, currency: 'ton' | 'stars', note?: string) {
    const response = await api.post('/api/user/deposit', {
      amount,
      currency,
      note
    });
    return response.data;
  }

  async makeCrashBet(amount: number, currency: 'stars' | 'ton') {
    const response = await api.post('/api/games/crash/bet', {
      amount,
      currency
    });
    return response.data;
  }

  async getReferralInfo() {
    const response = await api.get('/api/user/referral-info');
    return response.data;
  }
}

export const telegramService = new TelegramService();