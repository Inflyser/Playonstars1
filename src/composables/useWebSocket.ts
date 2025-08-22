import { apiMethods } from '@/services/api';

export const useApi = () => {
  // User methods
  const getProfile = () => apiMethods.get('/profile');
  const updateProfile = (data: any) => apiMethods.put('/profile', data);
  
  // Game methods
  const getCrashHistory = () => apiMethods.get('/crash/history');
  const placeCrashBet = (amount: number) => apiMethods.post('/crash/bet', { amount });
  
  const getCases = () => apiMethods.get('/cases');
  const openCase = (caseId: string) => apiMethods.post(`/cases/${caseId}/open`);
  
  // Leaderboard
  const getTopPlayers = () => apiMethods.get('/leaderboard/top');
  
  return {
    getProfile,
    updateProfile,
    getCrashHistory,
    placeCrashBet,
    getCases,
    openCase,
    getTopPlayers
  };
};