import { api } from './api';

export const checkBackendConnection = async (): Promise<boolean> => {
  try {
    console.log('Checking backend connection...');
    const response = await api.get('/');
    console.log('Backend response:', response.data);
    return true;
  } catch (error: any) {
    console.error('Backend connection failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    return false;
  }
};

export const checkAuthStatus = async (): Promise<boolean> => {
  try {
    const token = localStorage.getItem('telegram_token');
    if (!token) {
      console.log('No auth token found');
      return false;
    }

    console.log('Checking auth status...');
    const response = await api.get('/api/user/data');
    console.log('Auth check response:', response.data);
    return true;
  } catch (error: any) {
    console.error('Auth check failed:', error.message);
    return false;
  }
};