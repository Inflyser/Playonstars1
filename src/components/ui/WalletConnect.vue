<template>
    <div class="wallet-connect">
        <div v-if="!isConnected" class="connect-section">
            <h3>Connect TON Wallet</h3>
            
            <div v-if="isTelegramEnv" class="telegram-note">
                <p>⚠️ В Telegram WebApp подключение кошелька работает через внешнее приложение</p>
            </div>
            
            <button 
                @click="connect" 
                :disabled="isLoading"
                class="tg-button primary"
            >
                <span v-if="isLoading">Connecting...</span>
                <span v-else>{{ isTelegramEnv ? 'Open Tonkeeper' : 'Connect Wallet' }}</span>
            </button>
            
            <p>Connect your TON wallet to deposit and withdraw funds</p>
        </div>
        
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
import { ref, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useWalletStore } from '@/stores/useWalletStore';

const walletStore = useWalletStore();
const error = ref('');
const isTelegramEnv = ref(false);

onMounted(() => {
    // Проверяем что мы в Telegram WebApp
    isTelegramEnv.value = !!(window.Telegram && window.Telegram.WebApp);
    console.log('📱 Environment:', isTelegramEnv.value ? 'Telegram WebApp' : 'Browser');
});

const { isConnected, isLoading, shortAddress, formattedBalance } = storeToRefs(walletStore);

const connect = async () => {
    try {
        error.value = '';
        
        if (isTelegramEnv.value) {
            console.log('🔗 Opening TonConnect in Telegram...');
            // В Telegram WebApp可能需要 special handling
            window.open('https://app.tonkeeper.com/ton-connect', '_blank');
        }
        
        await walletStore.connect();
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