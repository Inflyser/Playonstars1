<template>
  <div class="home">
    <!-- Первый хедер (логотип и баланс) -->
    <header class="header-primary">
      <div class="header-content">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Play on Stars" />
          <span>Play on Stars</span>
        </div>
        <div class="balance">
          <span class="balance-label">Баланс:</span>
          <span class="balance-amount">1 000 ₽</span>
        </div>
      </div>
    </header>

    <!-- Второй хедер (аватар, никнейм, кнопка) -->
    <header class="header-secondary">
      <div class="header-content">
        <div class="user-info">
          <div class="avatar">
            <img src="@/assets/avatar.png" alt="Аватар" />
          </div>
          <div class="user-details">
            <span class="username">@username</span>
            <span class="balance-secondary">500 ₽</span>
          </div>
        </div>
        <button class="action-button">
          <i class="icon-plus"></i>
          Пополнить
        </button>
      </div>
    </header>

    <!-- Основной контент - две большие кнопки -->
    <main class="main-content">
      <div class="action-cards">
        <div class="action-card crash-card">
          <div class="card-content">
            <i class="card-icon">🎰</i>
            <h3>Crash Game</h3>
            <p>Испытай удачу!</p>
          </div>
        </div>

        <div class="action-card cases-card">
          <div class="card-content">
            <i class="card-icon">🎁</i>
            <h3>Кейсы</h3>
            <p>Открой и выиграй!</p>
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
// Теперь @/ указывает на папку src/
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 80px; /* Для плавающей навигации */
}

/* Первый хедер */
.header-primary {
  background: rgba(255, 255, 255, 0.1);
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

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-weight: bold;
  font-size: 18px;
}

.logo img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.balance {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  color: white;
}

.balance-label {
  font-size: 12px;
  opacity: 0.8;
}

.balance-amount {
  font-size: 16px;
  font-weight: bold;
}

/* Второй хедер */
.header-secondary {
  background: rgba(255, 255, 255, 0.15);
  padding: 20px 16px;
  margin-bottom: 24px;
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

.action-button {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
}

.cases-card {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(238, 90, 82, 0.3));
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