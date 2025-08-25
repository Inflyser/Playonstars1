<template>
  <div class="telegram-only">
    <div class="container">
      <div class="logo">
        <img src="@/assets/images/logo.svg" alt="PlayOnStars" />
        <h1>PlayOnStars</h1>
      </div>

      <div class="message">
        <div class="icon">📱</div>
        <h2>Доступно только в Telegram</h2>
        <p>Это приложение работает исключительно через Telegram Web App</p>
        
        <div class="instructions">
          <h3>Как получить доступ:</h3>
          <ol>
            <li>Откройте нашего бота в Telegram</li>
            <li>Нажмите кнопку "Start" или "Играть"</li>
            <li>Наслаждайтесь играми!</li>
          </ol>
        </div>

        <a :href="telegramBotUrl" class="tg-button">
          Перейти в Telegram
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const telegramBotUrl = computed(() => {
  const botUsername = '@Playonstars_bot'
  return `https://t.me/${botUsername}`
})
</script>

<style scoped>
.telegram-only {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.logo {
  margin-bottom: 30px;
}

.logo img {
  width: 80px;
  height: 80px;
  margin-bottom: 15px;
}

.logo h1 {
  color: #333;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.message .icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.message h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 15px;
  font-weight: 600;
}

.message p {
  color: #666;
  font-size: 16px;
  margin-bottom: 30px;
  line-height: 1.5;
}

.instructions {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin: 25px 0;
  text-align: left;
}

.instructions h3 {
  color: #333;
  font-size: 18px;
  margin-bottom: 15px;
  font-weight: 600;
}

.instructions ol {
  color: #666;
  padding-left: 20px;
  margin: 0;
}

.instructions li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.instructions li:last-child {
  margin-bottom: 0;
}

.tg-button {
  display: inline-block;
  background: #0088cc;
  color: white;
  padding: 16px 32px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.tg-button:hover {
  background: #006699;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 136, 204, 0.3);
}

/* Адаптивность */
@media (max-width: 480px) {
  .container {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .logo img {
    width: 60px;
    height: 60px;
  }
  
  .logo h1 {
    font-size: 24px;
  }
  
  .message h2 {
    font-size: 20px;
  }
  
  .tg-button {
    padding: 14px 28px;
    font-size: 15px;
  }
}
</style>