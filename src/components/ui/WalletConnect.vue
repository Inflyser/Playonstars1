<template>
  <div class="wallet-connect">
    <!-- Добавляем модалку -->
    <TonConnectModal ref="tonConnectModal" />
    
    <!-- Состояние: кошелек не подключен -->
    <div v-if="!isConnected" class="connect-section">
      <h3>Connect TON Wallet</h3>
      <button 
        @click="connect" 
        :disabled="isLoading"
        class="tg-button primary"
      >
        <span v-if="isLoading">Connecting...</span>
        <span v-else>Connect Wallet</span>
      </button>
      <p>Connect your TON wallet to deposit and withdraw funds</p>
    </div>
    
    <!-- Состояние: кошелек подключен -->
    <div v-else class="wallet-info">
      <h3>Connected Wallet</h3>
      <div class="wallet-details">
        <p><strong>Address:</strong> {{ shortAddress }}</p>
        <p><strong>Balance:</strong> {{ formattedBalance }} TON</p>
      </div>
      
      <div class="wallet-actions">
        <button @click="updateBalance" class="tg-button secondary">
          Refresh Balance
        </button>
        <button @click="disconnect" class="tg-button danger">
          Disconnect
        </button>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useWalletStore } from '@/stores/useWalletStore';
import { isTelegramWebApp } from '@/utils/telegram'; // ✅ Добавляем импорт
import TonConnectModal from '@/components/ui/TonConnectModal.vue';

const walletStore = useWalletStore();
const error = ref('');
const tonConnectModal = ref();

const { 
  isConnected, 
  isLoading, 
  shortAddress, 
  formattedBalance 
} = storeToRefs(walletStore);

const connect = async () => {
  try {
    error.value = '';
    
    // ✅ Используем импортированную функцию isTelegramWebApp()
    if (isTelegramWebApp()) {
      tonConnectModal.value?.open();
    } else {
      await walletStore.connect();
    }
  } catch (err) {
    error.value = 'Failed to connect wallet';
    console.error('Connection error:', err);
  }
};

const disconnect = () => {
  walletStore.disconnect();
};

const updateBalance = async () => {
  await walletStore.updateBalance();
};
</script>

<style scoped>

.wallet-connect {
    padding: 1rem;
    border: 1px solid var(--tg-theme-secondary-bg-color);
    border-radius: 8px;
    margin-bottom: 1rem;
}

.connect-section, .wallet-info {
    text-align: center;
}

.wallet-details {
    margin: 1rem 0;
    text-align: left;
}

.wallet-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
}

.error-message {
    color: var(--tg-theme-destructive-text-color);
    margin-top: 0.5rem;
    text-align: center;
}

.tg-button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: opacity 0.2s;
}

.tg-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.tg-button.primary {
    background-color: var(--tg-theme-button-color);
    color: var(--tg-theme-button-text-color);
}

.tg-button.secondary {
    background-color: var(--tg-theme-secondary-bg-color);
    color: var(--tg-theme-text-color);
}

.tg-button.danger {
    background-color: var(--tg-theme-destructive-bg-color);
    color: var(--tg-theme-destructive-text-color);
}
</style>