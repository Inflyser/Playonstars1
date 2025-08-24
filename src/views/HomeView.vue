<template>
  <div class="home">
    <!-- Первый хедер (логотип и панель с валютой) -->
    <header class="header-primary">
      <div class="header-content">
        <div class="logo">
          <img src="@/assets/images/logo.svg" alt="Play on Stars" />
        </div>
        <div class="currency-panel">
          <div class="currency-item">
            <img src="@/assets/images/flag.svg" alt="Флаг" class="flag-icon" />
          </div>
          <div class="currency-item">
            <img src="@/assets/images/wallet.svg" alt="Кошелек" class="wallet-icon" />
            <span class="balance-amount">1 000</span>
          </div>
          <div class="currency-item">
            <img src="@/assets/images/coin.svg" alt="Валюта" class="coin-icon" />
          </div>
        </div>
      </div>
    </header>

    <!-- Второй хедер (кнопка, аватар, баланс) -->
    <header class="header-secondary">
      <div class="header-content">
        <!-- Кнопка слева с иконкой -->
        <button class="action-button">
          <img src="@/assets/images/wallet-icon.svg" alt="Кошелек" class="button-icon" />
          Подключить кошелёк
        </button>
      
        <!-- Правая часть: юзернейм + баланс + аватар -->
        <div class="user-section">
          <!-- Текстовый блок -->
          <div class="user-text-info">
            <div class="username-line">
              <span class="username">@username</span>
            </div>
            <div class="balance-line">
              <span class="balance-secondary">0.001</span>
              <div class="balance-buttons">
                <button class="mini-button">
                  <img src="@/assets/images/plus-small.svg" alt="Добавить" />
                </button>
                <button class="mini-button">
                  <img src="@/assets/images/refresh-small.svg" alt="Обновить" />
                </button>
              </div>
            </div>
          </div>

          <!-- Аватар -->
          <div class="avatar">
            <img src="@/assets/images/avatar.png" alt="Аватар" />
          </div>
        </div>
      </div>
    </header>

    <!-- Основной контент - две большие кнопки -->
    <main class="main-content">
      <div class="action-cards">
        <!-- Space Monkey карточка -->
        <div class="action-card space-monkey-card">
          <!-- Слой 4: Цветной фон -->
          <div class="card-color-bg"></div>

          <!-- Слой 3: Фоновая картинка -->
          <img src="@/assets/images/space-monkey-bg.svg" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/space-monkey-character.svg" alt="Space Monkey" class="card-main-image" />

          <!-- Слой 1: Текст -->
          <div class="card-content">
            <h3>Space Monkey</h3>
            <p>Ставь ставку и сражайся с другими игроками</p>
          </div>
        </div>
      
        <!-- PvP арена карточка -->
        <div class="action-card pvp-arena-card">
          <!-- Слой 4: Цветной фон -->
          <div class="card-color-bg"></div>

          <!-- Слой 3: Фоновая картинка -->
          <img src="@/assets/images/pvp-arena-bg.svg" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/pvp-arena-character.svg" alt="PvP Арена" class="card-main-image" />

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

.currency-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  background-color: #100D1F;
  padding: 5px;
  border-radius: 10px;
}

.currency-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

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
}


/* Второй хедер */
.header-secondary {
  background: #180A24;
  padding: 5px 16px 14px 16px;
  margin-bottom: 22px;
  border-bottom: 1px solid #25213C;
}

.header-secondary .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center; /* ← ВАЖНО: выравнивание по центру вертикально */
  gap: 20px;
}

/* Кнопка слева с иконкой */
.action-button {
  margin: 10px 0px 0px 0px;
  background: #00A6FC;
  color: white;
  border: none;
  padding: 0px 20px;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  white-space: nowrap;
  height: 38px; /* ← Фиксированная высота для выравнивания */
  box-sizing: border-box;
}

/* Правая секция - выравнивание по центру */
.user-section {
  display: flex;
  align-items: center; /* ← Выравнивание по центру */
  gap: 12px;
  height: 100%;
}

/* Остальные стили остаются без изменений */
.user-text-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.username-line {
  margin-bottom: 0px;
}

.username {
  font-weight: bold;
  font-size: 12px;
  color: #A2A2A2;
}

.balance-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.balance-secondary {
  font-size: 12px;
  font-weight: bold;
  color: #ffffff;
}

.balance-buttons {
  display: flex;
  gap: 4px;
}

.mini-button {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 6px;
  width: 16px;
  height: 0px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mini-button:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.mini-button img {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.avatar img {
  margin: 0px 0px -10px 0px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

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
  overflow: hidden; /* ← ВАЖНО! Это обрезает выступающие части */
  cursor: pointer;
  height: 150px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

/* Слой 4: Цветной фон */
.card-color-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.space-monkey-card .card-color-bg {
  background: #00A051; /* Синий градиент */
}

.pvp-arena-card .card-color-bg {
  background: #F8A820 /* Красный градиент */
}

/* Слой 3: Фоновая картинка */
.card-bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 2;
}

/* Слой 2: Основная картинка */
.card-main-image {
  position: absolute;
  right: -10px; /* Выступает за правый край */
  bottom: -10px; /* Выступает за нижний край */
  height: 120%; /* Значительно больше кнопки */
  width: auto;
  object-fit: contain;
  z-index: 3;
  transition: all 0.3s ease;
  filter: drop-shadow(0 5px 20px rgba(0, 0, 0, 0.6));
  transform-origin: right bottom; /* Точка трансформации */
}


/* Слой 1: Текст */
.card-content {
  position: relative;
  z-index: 4;
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
}

.card-content h3 {
  margin: 40px 0 12px 0;
  font-size: 30px;
  font-weight: bold;
  color: #ffffff;
}

.card-content p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  max-width: 60%;
  line-height: 1.5;
}

/* Градиент overlay для лучшей читаемости текста */


@media (max-width: 480px) {
  .action-card {
    height: 150px;
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

@media (max-width: 480px) {
  .card-main-image {
    height: 120%;
    right: 0px;
    bottom: -32px;
  }
}
</style>