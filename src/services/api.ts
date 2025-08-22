import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-api.com';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Интерцептор для ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

// Базовые методы
export const apiMethods = {
  async get(url: string) {
    const response = await api.get(url);
    return response.data;
  },

  async post(url: string, data: any) {
    const response = await api.post(url, data);
    return response.data;
  },

  async put(url: string, data: any) {
    const response = await api.put(url, data);
    return response.data;
  },

  async delete(url: string) {
    const response = await api.delete(url);
    return response.data;
  }
};