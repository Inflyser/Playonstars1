// stores/useLanguageStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'
import { i18n } from '@/main'

// ✅ Создаем тип для поддерживаемых языков
export type AppLanguage = 'ru' | 'en' | 'cn'

export const useLanguageStore = defineStore('language', () => {
  // ✅ Указываем конкретный тип вместо string
  const currentLanguage = ref<AppLanguage>('ru')
  const isLoading = ref(false)

  const loadLanguage = async (): Promise<void> => {
    try {
      isLoading.value = true
      const response = await api.get('/api/user/language')
      
      if (response.data.language) {
        const lang = response.data.language as AppLanguage // ✅ Приводим тип
        if (['ru', 'en', 'cn'].includes(lang)) {
          currentLanguage.value = lang
          i18n.global.locale.value = lang // ✅ Теперь типы совпадают
        }
      }
    } catch (error) {
      console.error('Ошибка при загрузке языка:', error)
      currentLanguage.value = 'ru'
      i18n.global.locale.value = 'ru'
    } finally {
      isLoading.value = false
    }
  }

  const setLanguage = async (lang: AppLanguage): Promise<boolean> => { // ✅ Меняем тип параметра
    try {
      isLoading.value = true
      const response = await api.post('/api/user/language', { language: lang })
      
      if (response.status === 200) {
        currentLanguage.value = lang
        i18n.global.locale.value = lang // ✅ Теперь типы совпадают
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