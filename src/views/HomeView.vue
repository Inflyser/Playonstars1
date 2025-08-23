<template>
  <div class="home">
    <!-- Первый хедер (логотип и панель с валютой) -->
    <header class="header-primary">
      <div class="header-content">
        <div class="logo">
          <img src="@/assets/images/logo.png" alt="Play on Stars" />
        </div>
        <div class="currency-panel">
          <div class="currency-item">
            <img src="@/assets/images/flag.png" alt="Флаг" class="flag-icon" />
          </div>
          <div class="currency-item">
            <img src="@/assets/images/wallet.png" alt="Кошелек" class="wallet-icon" />
            <span class="balance-amount">1 000</span>
          </div>
          <div class="currency-item">
            <img src="@/assets/images/coin.png" alt="Валюта" class="coin-icon" />
          </div>
        </div>
      </div>
    </header>

    <!-- Второй хедер (кнопка, аватар, баланс) -->
    <header class="header-secondary">
      <div class="header-content">
        <button class="action-button">
          <i class="icon-plus"></i>
          Подключить кошелёк
        </button>
        <div class="user-info">
          <div class="avatar">
            <img src="@/assets/images/avatar.png" alt="Аватар" />
          </div>
          <div class="user-details">
            <span class="username">@username</span>
            <span class="balance-secondary">500</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Основной контент - две большие кнопки -->
    <main class="main-content">
      <div class="action-cards">
        <div class="action-card crash-card">
          <div class="card-content">
            <i class="card-icon">🎰</i>
            <h3>Space Monkey</h3>
            <p>Ставь ставку и сражайся с другими игрокам</p>
          </div>
        </div>

        <div class="action-card cases-card">
          <div class="card-content">
            <i class="card-icon">🎁</i>
            <h3>PvP-арена</h3>
            <p>Сражайся с игроками и побеждай!</p>
          </div>
        </div>
      </div>
    </main>

    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #180A24;
  padding-bottom: 80px;
}

/* Первый хедер */
.header-primary {
  background: #180A24;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 16px;
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

.currency-panel {
  display: flex;
  align-items: center;
  gap: 16px;
}

.currency-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.flag-icon,
.wallet-icon,
.coin-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.balance-amount {
  font-size: 16px;
  font-weight: bold;
  color: white;
}

/* Второй хедер */
.header-secondary {
  background: #180A24;
  padding: 20px 16px;
  margin-bottom: 24px;
}

.header-secondary .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-button {
  background: #00A6FC;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.action-button:hover {
  transform: translateY(-2px);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid white;
}

.user-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.username {
  font-weight: bold;
  font-size: 16px;
}

.balance-secondary {
  font-size: 14px;
  opacity: 0.9;
}

/* Основной контент */
.main-content {
  padding: 0 16px;
}

.action-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.action-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.2);
}

.crash-card {
  background: #00A051;
}

.cases-card {
  background: #FDB423;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.card-icon {
  font-size: 48px;
}

.action-card h3 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.action-card p {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

/* Адаптивность */
@media (min-width: 768px) {
  .action-cards {
    grid-template-columns: 1fr 1fr;
  }
  
  .header-content {
    padding: 0 32px;
  }
  
  .main-content {
    padding: 0 32px;
  }
}
</style>