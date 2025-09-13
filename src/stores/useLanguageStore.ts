// stores/useLanguageStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const useLanguageStore = defineStore('language', () => {
  const currentLanguage = ref('ru')
  const isLoading = ref(false)

  const loadLanguage = async (): Promise<boolean> => {
    try {
      isLoading.value = true
      const response = await api.get('/api/user/language')
      if (response.data.language) {
        currentLanguage.value = response.data.language
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to load language:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const setLanguage = async (lang: string): Promise<boolean> => {
    try {
      isLoading.value = true
      const response = await api.post('/api/user/language', { language: lang })
      
      if (response.status === 200) {
        currentLanguage.value = lang
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to save language:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    currentLanguage,
    isLoading,
    loadLanguage,
    setLanguage
  }
})