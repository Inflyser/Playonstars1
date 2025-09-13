// stores/useLanguageStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const useLanguageStore = defineStore('language', () => {
  const currentLanguage = ref('ru')
  const isLoading = ref(false)

  const loadLanguage = async () => {
    try {
      isLoading.value = true
      const response = await api.get('/api/user/language')
      if (response.data.language) {
        currentLanguage.value = response.data.language
      }
    } catch (error) {
      console.error('Failed to load language:', error)
    } finally {
      isLoading.value = false
    }
  }

  const setLanguage = async (lang: string) => {
    try {
      isLoading.value = true;
      // Ждем подтверждения от бэкенда
      await api.post('/api/user/language', { language: lang });
      // Только затем обновляем состояние
      currentLanguage.value = lang;
    } catch (error) {
      console.error('Failed to save language:', error);
      throw error; // Пробрасываем ошибку, чтобы обработать её в компоненте
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentLanguage,
    isLoading,
    loadLanguage,
    setLanguage
  }
})