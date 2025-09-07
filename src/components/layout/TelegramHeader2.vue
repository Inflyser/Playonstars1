<template>
    <header class="header-secondary">
      <div class="header-content">
        <!-- Кнопка/адрес кошелька слева -->
        <div class="wallet-section">
          <button 
            v-if="!walletStore.isConnected" 
            @click="connectWallet"
            class="action-button"
            :disabled="walletStore.isLoading"
          >
            <img src="@/assets/images/wallet-icon.svg" alt="Кошелек" class="button-icon" />
            {{ walletStore.isLoading ? 'Подключение...' : 'Подключить кошелёк' }}
          </button>
          
          <div v-else class="wallet-address">
            {{ walletStore.shortAddress }}
          </div>
        </div>
      
        <!-- Правая часть: юзернейм + баланс + аватар -->
        <div class="user-section">
          <!-- Текстовый блок -->
          <div class="user-text-info">
            <div class="username-line">
              <span class="username">@{{ userStore.user?.username || userStore.telegramUser?.username }}</span>
            </div>
            <div class="balance-line">
              <span class="balance-secondary">{{ userStore.balance.ton_balance }}</span>
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
import { useWalletStore } from '@/stores/useWalletStore'; // Импортируем хранилище кошелька
import { onMounted } from 'vue';

const userStore = useUserStore();
const walletStore = useWalletStore();

// Инициализируем кошелек при монтировании компонента
onMounted(async () => {
  if (!walletStore.isInitialized) {
    await walletStore.init();
  }
});

const connectWallet = async () => {
  try {
    await walletStore.connect();
    // После подключения можно обновить баланс
    await userStore.fetchBalance();
  } catch (error) {
    console.error('Ошибка подключения кошелька:', error);
  }
};
</script>

<style scoped>
/* Стили остаются без изменений */
.header-secondary {
  padding: 5px 16px 14px 16px;
  margin-bottom: 22px;
  border-bottom: 1px solid #25213C;
}

.header-secondary .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

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
  height: 38px;
  box-sizing: border-box;
}

.wallet-address {
  margin: 10px 0px 0px 0px;
  padding: 0px 20px;
  color: #00A6FC;
  font-weight: bold;
  font-size: 14px;
  height: 38px;
  display: flex;
  align-items: center;
  background: rgba(0, 166, 252, 0.1);
  border-radius: 25px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 100%;
}

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