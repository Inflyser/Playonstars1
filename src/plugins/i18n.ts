// plugins/i18n.ts
import { App } from 'vue'
import { useLanguageStore } from '@/stores/useLanguageStore'
import { translations } from '@/locales'

// Типы для переводов
type TranslationKey = keyof typeof translations.ru

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $t: (key: TranslationKey) => string
    $language: string
  }
}

export default {
  install: (app: App) => {
    const languageStore = useLanguageStore()
    
    app.config.globalProperties.$t = (key: TranslationKey) => {
      const currentLang = languageStore.currentLanguage
      const translation = translations[currentLang as keyof typeof translations]
      return translation[key] || key
    }
    
    app.config.globalProperties.$language = languageStore.currentLanguage
  }
}