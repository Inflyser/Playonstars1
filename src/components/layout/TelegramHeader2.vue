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
            {{ walletStore.isLoading ? 'Подключение...' : $t('wallet') }}
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
      <!-- Уведомление о подключении -->

</template>

<script setup lang="ts">
import TGButton from '@/components/ui/TGButton.vue'
import { useUserStore } from '@/stores/useUserStore';
import { useWalletStore } from '@/stores/useWalletStore';
import { ref, watch } from 'vue';


const userStore = useUserStore();
const walletStore = useWalletStore();
const showSuccessNotification = ref(false);

// Следим за изменениями статуса подключения
watch(() => walletStore.isConnected, (newVal, oldVal) => {
  if (newVal && !oldVal) {
    // Показываем уведомление при успешном подключении
    showSuccessNotification.value = true;
    setTimeout(() => {
      showSuccessNotification.value = false;
    }, 3000);
    
    // Обновляем баланс
    userStore.fetchBalance();
  }
});



const connectWallet = async () => {
  try {
    await walletStore.connect();
  } catch (error) {
    console.error('Ошибка подключения кошелька:', error);
  }
};
</script>

<style scoped>
/* Существующие стили остаются */
.header-secondary {
  padding: 5px 16px 14px 16px;
  margin-bottom: 22px;
  border-bottom: 1px solid #25213C;
  position: relative;
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
  color: #ffffff;
  font-weight: bold;
  font-size: 14px;
  height: 38px;
  display: flex;
  align-items: center;
  background: #534081B2;
  border-radius: 25px;
  gap: 8px;
}

.connected-badge {
  color: #4CAF50;
  font-weight: bold;
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

/* Уведомление */
.notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  z-index: 1000;
  animation: slideDown 0.3s ease;
}

.notification.success {
  background: #4CAF50;
  color: white;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>