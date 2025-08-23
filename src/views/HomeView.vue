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
        <!-- Space Monkey карточка -->
        <div class="action-card space-monkey-card">
          <!-- Слой 3: Фон -->
          <img src="@/assets/images/space-monkey-bg.png" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/space-monkey-character.png" alt="Space Monkey" class="card-main-image" />

          <!-- Слой 1: Текст -->
          <div class="card-content">
            <h3>Space Monkey</h3>
            <p>Ставь ставку и сражайся с другими игроками</p>
          </div>
        </div>
      
        <!-- PvP арена карточка -->
        <div class="action-card pvp-arena-card">
          <!-- Слой 3: Фон -->
          <img src="@/assets/images/pvp-arena-bg.png" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/pvp-arena-character.png" alt="PvP Арена" class="card-main-image" />

          <!-- Слой 1: Текст -->
          <div class="card-content">
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
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  height: 200px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

/* Слой 3: Фоновая картинка */
.card-bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  filter: brightness(0.7) blur(2px);
}

/* Слой 2: Основная картинка */
.card-main-image {
  position: absolute;
  right: 20px;
  bottom: 20px;
  height: 80%;
  object-fit: contain;
  z-index: 2;
  transition: transform 0.3s ease;
}

.action-card:hover .card-main-image {
  transform: scale(1.05) translateY(-5px);
}

/* Слой 1: Текст */
.card-content {
  position: relative;
  z-index: 3;
  padding: 30px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
}

.card-content h3 {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}

.card-content p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  max-width: 60%;
  line-height: 1.5;
}

/* Градиент overlay для лучшей читаемости текста */
.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.6) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.2) 100%
  );
  z-index: 2;
}

/* Адаптивность */
@media (min-width: 768px) {
  .action-cards {
    grid-template-columns: 1fr 1fr;
  }
  
  .action-card {
    height: 240px;
  }
  
  .card-content h3 {
    font-size: 32px;
  }
  
  .card-content p {
    font-size: 18px;
  }
  
  .card-main-image {
    right: 30px;
    bottom: 30px;
    height: 85%;
  }
}

@media (max-width: 480px) {
  .action-card {
    height: 180px;
  }
  
  .card-content {
    padding: 20px;
  }
  
  .card-content h3 {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .card-content p {
    font-size: 14px;
    max-width: 70%;
  }
  
  .card-main-image {
    right: 15px;
    bottom: 15px;
    height: 70%;
  }
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