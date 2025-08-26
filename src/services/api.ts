import axios from 'axios'

const API_BASE_URL = 'https://playonstars.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

// Простая функция для теста
export const testConnection = async () => {
  try {
    const response = await api.get('/api/test')
    return response.data
  } catch (error) {
    console.log('Using mock data - backend unavailable')
    return { status: 'mock', message: 'Backend not available' }
  }
}

export default api