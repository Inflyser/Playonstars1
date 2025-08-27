<template>
    <header class="header-primary">
      <div class="header-content">
        <div class="logo">
          <img src="@/assets/images/logo.svg" alt="Play on Stars" />
        </div>

        <div class="currency-panel">
          <!-- Левая часть: только флаг -->
          <div class="currency-section flag-section">
            <img src="@/assets/images/flag.svg" alt="Флаг" class="flag-icon" />
          </div>

          <!-- Разделитель -->
          <div class="divider"></div>

          <!-- Правая часть: кошелек, баланс, валюта -->
          <div class="currency-section wallet-section">
            <img src="@/assets/images/wallet.svg" alt="Кошелек" class="wallet-icon" />
            <span class="balance-amount">{{ userStore.balance.ton_balance }}</span>
            <img src="@/assets/images/coin.svg" alt="Валюта" class="coin-icon" />
          </div>
        </div>
      </div>
    </header>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/useUserStore';
const userStore = useUserStore();
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
  gap: 0; /* Убираем gap, так как есть разделитель */
  background-color: #100D1F;
  padding: 0;
  border-radius: 10px;
}

/* Общие стили для обеих секций */
.currency-section {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  height: 100%;
}

/* Левая секция (только флаг) */
.flag-section {
  height: 3.5vh;
  margin: 5px;
  border-radius: 50px 50px 50px 50px;
  background-color: #241D49;
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
}


</style>