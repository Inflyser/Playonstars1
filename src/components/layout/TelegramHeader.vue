<template>
  <header class="header-primary">
    <div class="header-content">
      <div class="logo">
        <img src="@/assets/images/logo.svg" alt="Play on Stars" />
      </div>

      <div class="currency-panel">
        <!-- Левая часть: только флаг (теперь кнопка) -->
        <button class="currency-section flag-section" @click="toggleLanguageSelector">
          <img src="@/assets/images/flag.svg" alt="Флаг" class="flag-icon" />
        </button>

        <!-- Разделитель -->
        <div class="divider" v-if="!showLanguageSelector"></div>

        <!-- Правая часть: кошелек, баланс, валюта (скрывается при выборе языка) -->
        <div class="currency-section wallet-section" v-if="!showLanguageSelector">
          <img src="@/assets/images/wallet.svg" alt="Кошелек" class="wallet-icon" />
          <span class="balance-amount">{{ userStore.balance.stars_balance }}</span>
          <img src="@/assets/images/coin.svg" alt="Валюта" class="coin-icon" />
        </div>

        <!-- Панель выбора языка (появляется при нажатии на флаг) -->
        <div class="language-selector" v-if="showLanguageSelector">
          <button 
            class="language-option selected" 
            @click="selectLanguage('ru')"
            aria-label="Русский язык"
          >
            <img src="@/assets/images/flag.svg" alt="Русский" />
          </button>
          <button 
            class="language-option" 
            @click="selectLanguage('en')"
            aria-label="Английский язык"
          >
            <img src="@/assets/images/united_kingdom.svg" alt="Английский" />
          </button>
          <button 
            class="language-option" 
            @click="selectLanguage('cn')"
            aria-label="Китайский язык"
          >
            <img src="@/assets/images/vietnam.svg" alt="Китайский" />
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/useUserStore';

const userStore = useUserStore();
const showLanguageSelector = ref(false);
const currentLanguage = ref('ru'); // По умолчанию русский

const toggleLanguageSelector = () => {
  showLanguageSelector.value = !showLanguageSelector.value;
};

const selectLanguage = (lang: string) => {
  currentLanguage.value = lang;
  // Здесь будет логика смены языка
  setTimeout(() => {
    showLanguageSelector.value = false;
  }, 300); // Небольшая задержка для визуального подтверждения выбора
};
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