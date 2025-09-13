<template>
  <header class="header-primary">
    <div class="header-content">
      <div class="logo">
        <img src="@/assets/images/logo.svg" />
      </div>

      <div class="currency-panel">
        <button 
          class="currency-section flag-section" 
          @click="toggleLanguageSelector"
          :disabled="languageStore.isLoading"
        >
          <img :src="currentFlag" :alt="languageStore.currentLanguage" class="flag-icon" />
          <span v-if="languageStore.isLoading" class="loading-spinner">⟳</span>
        </button>

        <div class="divider" v-if="!showLanguageSelector && !languageStore.isLoading"></div>

        <div class="currency-section wallet-section" v-if="!showLanguageSelector && !languageStore.isLoading">
          <img src="@/assets/images/wallet.svg" class="wallet-icon" />
          <span class="balance-amount">{{ userStore.balance.stars_balance }}</span>
          <img src="@/assets/images/coin.svg" class="coin-icon" />
        </div>

        <div class="language-selector" v-if="showLanguageSelector && !languageStore.isLoading">
          <button 
            v-for="lang in languages" 
            :key="lang.code"
            class="language-option" 
            :class="{ 
              selected: lang.code === languageStore.currentLanguage,
              loading: languageStore.isLoading
            }"
            @click="selectLanguage(lang.code)"
            :disabled="languageStore.isLoading"
            :aria-label="lang.name"
          >
            <img :src="lang.flag" :alt="lang.name" />
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useLanguageStore } from '@/stores/useLanguageStore'

const userStore = useUserStore()
const languageStore = useLanguageStore()
const showLanguageSelector = ref(false)

import flagRu from '@/assets/images/flag.svg'
import flagEn from '@/assets/images/united_kingdom.svg'
import flagCn from '@/assets/images/vietnam.svg'

const languages = [
  { code: 'ru', name: 'Русский', flag: flagRu },
  { code: 'en', name: 'English', flag: flagEn },
  { code: 'cn', name: '中文', flag: flagCn }
]

const currentFlag = computed(() => {
  const lang = languages.find(l => l.code === languageStore.currentLanguage)
  return lang ? lang.flag : flagRu
})


const toggleLanguageSelector = () => {
  if (!languageStore.isLoading) {
    showLanguageSelector.value = !showLanguageSelector.value
  }
}

const selectLanguage = async (lang: string) => {
  if (languageStore.isLoading || lang === languageStore.currentLanguage) {
    showLanguageSelector.value = false
    return
  }

  try {
    // Ждем завершения сохранения языка
    const success = await languageStore.setLanguage(lang)
    
    if (success) {
      showLanguageSelector.value = false
      // УБИРАЕМ принудительную перезагрузку!
      // Переводы должны обновляться реактивно через ваш i18n плагин
    } else {
      console.error('Language change failed')
    }
  } catch (error) {
    console.error('Failed to change language:', error)
    showLanguageSelector.value = false
  }
}


</script>

<style scoped>
/* Первый хедер */
.header-primary {
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #25213C;
  padding: 16px 16px 10px 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.logo img {
  width: 136px;
  height: 28px;
  border-radius: 8px;
}

/* Общая панель валют */
.currency-panel {
  display: flex;
  align-items: center;
  gap: 0;
  background-color: #100D1F;
  padding: 0;
  border-radius: 10px;
  position: relative;
  min-height: 40px;
}

/* Общие стили для обеих секций */
.currency-section {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  height: 100%;
}

/* Кнопка флага */
.flag-section {
  height: 3.5vh;
  margin: 5px;
  border-radius: 50px;
  background-color: #241D49;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.flag-section:hover {
  background-color: #352a6b;
  transform: scale(1.05);
}

/* Правая секция (кошелек + баланс + валюта) */
.wallet-section {
  height: 3.5vh;
  margin: 5px;
  border-radius: 50px 40px 40px 50px;
  background-color: #241D49;
}

/* Вертикальный разделитель */
.divider {
  width: 1.5px;
  height: 20px;
  border-radius: 50%;
  background: #241D49;
}

/* Иконки */
.flag-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
}

.wallet-icon {
  width: 14px;
  height: 14px;
}

.coin-icon {
  width: 12px;
  height: 12px;
}

.balance-amount {
  font-size: 12px;
  font-weight: bold;
  color: white;
  margin: 0px 0px 1px 0px;
}

/* Панель выбора языка */
.language-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  animation: fadeIn 0.3s ease;
}

.language-option {
  background: none;
  border: 2px solid transparent;
  border-radius: 50%;
  padding: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.language-option:hover {
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.language-option.selected {
  border-color: #6C5DD3;
  box-shadow: 0 0 8px rgba(108, 93, 211, 0.6);
}

.language-option img {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}

/* Анимация появления */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .currency-section {
    padding: 6px 10px;
  }
  
  .flag-icon {
    width: 16px;
    height: 16px;
  }
  
  .wallet-icon,
  .coin-icon {
    width: 12px;
    height: 12px;
  }
  
  .balance-amount {
    font-size: 11px;
  }
  
  .language-option {
    width: 28px;
    height: 28px;
  }
  
  .language-option img {
    width: 16px;
    height: 16px;
  }
}
</style>