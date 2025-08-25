import axios from 'axios'

const API_BASE_URL = 'https://playonstars.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Для кук и сессий
})

// Интерцептор для ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Перенаправляем на страницу только для Telegram
      if (window.location.pathname !== '/telegram-only') {
        window.location.href = '/telegram-only'
      }
    }
    return Promise.reject(error)
  }
)

export default api