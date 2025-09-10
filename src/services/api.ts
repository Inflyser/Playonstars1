import axios from 'axios';

const API_BASE_URL = 'https://playonstars.onrender.com';

console.log('API Base URL:', API_BASE_URL); // Добавьте это

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Интерцептор для логирования запросов
api.interceptors.request.use((config) => {
  console.log('Making request to:', config.url);
  
  const token = localStorage.getItem('telegram_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('Authorization header set');
  } else {
    console.log('No auth token found');
  }
  
  return config;
});

// Интерцептор для логирования ответов
api.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('Request failed:', error.response?.status, error.message);
    if (error.response?.status === 401) {
      localStorage.removeItem('telegram_token');
      console.log('Token removed due to 401');
    }
    return Promise.reject(error);
  }
);