import axios from 'axios'

const API_BASE_URL = 'https://playonstars.onrender.com'

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Важно для сессий и куков
});

// Интерцептор для добавления заголовков
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('telegram_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('telegram_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);