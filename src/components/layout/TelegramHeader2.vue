<template>
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
              <span class="username">@{{ userStore.user?.username || userStore.telegramUser?.username }}</span>
            </div>
            <div class="balance-line">
              <span class="balance-secondary">{{ userStore.balance.stars_balance }}</span>
              <div class="balance-buttons">
                <TGButton />
              </div>
            </div>
          </div>

          <!-- Аватар -->
          <div class="avatar">
            <img :src="userStore.getAvatarUrl" />
          </div>
        </div>
      </div>
    </header>
</template>

<script setup lang="ts">
import TGButton from '@/components/ui/TGButton.vue'
import { useUserStore } from '@/stores/useUserStore';
const userStore = useUserStore();
</script>

<style scoped>
/* Второй хедер */
.header-secondary {
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



.avatar img {
  margin: 0px 0px -10px 0px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}
</style>