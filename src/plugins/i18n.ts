// plugins/i18n.ts
import { App, watch } from 'vue'
import { useLanguageStore } from '@/stores/useLanguageStore'
import { translations } from '@/locales'

export default {
  install: (app: App) => {
    const languageStore = useLanguageStore()
    
    // Реактивная функция для переводов
    const translate = (key: string) => {
      const currentLang = languageStore.currentLanguage
      const translation = translations[currentLang as keyof typeof translations]
      return translation[key as keyof typeof translation] || key
    }
    
    app.config.globalProperties.$t = translate
    app.config.globalProperties.$language = languageStore.currentLanguage
    
    // Следим за изменением языка и принудительно обновляем компоненты
    watch(() => languageStore.currentLanguage, (newLang) => {
      // Принудительно обновляем все компоненты
      app.config.globalProperties.$t = translate
      app.config.globalProperties.$language = newLang
      
      // Триггерим обновление
      app.mixin({
        updated() {
          this.$forceUpdate()
        }
      })
    })
  }
}