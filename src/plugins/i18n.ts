// plugins/i18n.ts
import { App } from 'vue'
import { useLanguageStore } from '@/stores/useLanguageStore'

export default {
  install: (app: App) => {
    const languageStore = useLanguageStore()
    
    // Глобальная переменная для доступа к языку
    app.config.globalProperties.$t = (key: string) => {
      // Здесь можно реализовать переводы
      return key
    }
    
    app.config.globalProperties.$language = languageStore.currentLanguage
  }
}