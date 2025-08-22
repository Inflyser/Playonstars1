import { api } from '@/services/api';

export const useApi = () => {
  const getProfile = async () => {
    const response = await api.get('/profile');
    return response.data;
  };

  const updateBalance = async (amount: number) => {
    const response = await api.post('/balance/update', { amount });
    return response.data;
  };

  const getCrashHistory = async () => {
    const response = await api.get('/crash/history');
    return response.data;
  };

  return { getProfile, updateBalance, getCrashHistory };
};