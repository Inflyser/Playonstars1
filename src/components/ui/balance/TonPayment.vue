<template>
    <div class="ton-payment">
        <TonConnectModal ref="tonConnectModal" />
        
        <!-- Состояние: кошелек не подключен -->
        <div v-if="!isConnected" class="connect-section">
            <div class="connect-header">
                <img src="@/assets/images/ton.svg" alt="TON" class="ton-logo" />
                <h3>Подключите TON кошелек</h3>
            </div>
            <p>Для пополнения баланса подключите ваш TON кошелек</p>
            <button 
                @click="connectWallet" 
                :disabled="isLoading"
                class="btn connect-btn"
            >
                <span v-if="isLoading">Подключение...</span>
                <span v-else>Подключить кошелек</span>
            </button>
        </div>

        <!-- Состояние: кошелек подключен -->
        <div v-else class="payment-section">
            <div class="wallet-info">
                <div class="wallet-header">
                    <span>Подключенный кошелек:</span>
                    <span class="wallet-address">{{ shortAddress }}</span>
                </div>
                <div class="balance-info">
                    <span>Баланс кошелька:</span>
                    <span class="balance-amount">{{ formattedBalance }} TON</span>
                </div>
            </div>

            <InputPanel
                v-model="amount"
                :prefix-text="'TON'"
                :placeholder="'Введите сумму в TON'"
                :max-value="maxAmount"
                :icon-type="'ton'"
            />
            
            <p style="color: #6A717B; font-size: 13px; margin: -10px 10px 15px 20px;">
                Минимальная сумма: 0.1 TON
            </p>

            <div class="two-buttons-container">
                <button class="btn primary" @click="$router.back()">Отмена</button>
                <button 
                    class="btn secondary" 
                    @click="deposit"
                    :disabled="!isValidAmount || isProcessing"
                >
                    <span v-if="isProcessing">Обработка...</span>
                    <span v-else>Пополнить</span>
                </button>
            </div>

            <!-- Кнопка отключения кошелька -->
            <button class="disconnect-btn" @click="disconnectWallet">
                Отключить кошелек
            </button>
        </div>

        <!-- Модальное окно подтверждения -->
        <div v-if="showConfirmation" class="modal-overlay">
            <div class="confirmation-modal">
                <h3>Подтверждение перевода</h3>
                <p>Вы собираетесь перевести {{ amount }} TON на адрес:</p>
                <p class="wallet-address-confirm">{{ appWalletAddress }}</p>
                <div class="modal-buttons">
                    <button @click="showConfirmation = false" class="btn cancel">Отмена</button>
                    <button @click="confirmDeposit" class="btn confirm">Подтвердить</button>
                </div>
            </div>
        </div>

        <!-- Уведомления -->
        <div v-if="error" class="error-message">
            {{ error }}
        </div>
        <div v-if="successMessage" class="success-message">
            {{ successMessage }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import InputPanel from '@/components/layout/InputPanel.vue'
import { useWalletStore } from '@/stores/useWalletStore'
import { useUserStore } from '@/stores/useUserStore'
import { api } from '@/services/api'
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram'
import TonConnectModal from '@/components/ui/TonConnectModal.vue'
import { tonConnectService } from '@/services/tonconnect';

import { transactionWatcher } from '@/services/transactionWatcher';

const router = useRouter()
const walletStore = useWalletStore()
const userStore = useUserStore()
const tonConnectModal = ref()

const { 
    isConnected, 
    isLoading, 
    shortAddress, 
    formattedBalance, 
    tonBalance 
} = storeToRefs(walletStore)

const amount = ref('')
const isProcessing = ref(false)
const error = ref('')
const successMessage = ref('')
const showConfirmation = ref(false)
const appWalletAddress = ref(import.meta.env.VITE_APP_WALLET_ADDRESS || 'UQDrohhgJWapIy_zUhZMAby7BjgsrN3gt5rNlC6KByB27eXk')

// Вычисляемые свойства
const maxAmount = computed(() => tonBalance.value?.toString() || '1000')
const isValidAmount = computed(() => {
    const numAmount = parseFloat(amount.value || '0')
    return numAmount >= 0.1 && numAmount <= (tonBalance.value || 0)
})

// Метод для создания платежной ссылки
const createTelegramPaymentLink = (amount: number): string => {
    const appWallet = appWalletAddress.value;
    const userTelegramId = userStore.user?.telegram_id;
    const comment = `deposit:${userTelegramId}`;
    
    const nanoAmount = Math.floor(amount * 1e9).toString();
    return `tg://wallet?startapp=transfer=${appWallet}_${nanoAmount}_${encodeURIComponent(comment)}`;
};

// Методы
const connectWallet = async () => {
    console.log('🎯 [TonPayment] Connect wallet button clicked!');
    try {
        error.value = '';
        console.log('📱 [TonPayment] Is Telegram environment:', isTelegramWebApp());
        
        if (isTelegramWebApp()) {
            console.log('📲 [TonPayment] Opening modal...');
            tonConnectModal.value?.open();
            console.log('✅ [TonPayment] Modal opened successfully');
        } else {
            console.log('🌐 [TonPayment] Connecting directly via wallet store...');
            await walletStore.connect();
            console.log('✅ [TonPayment] Wallet store connect completed');
        }
    } catch (err: any) {
        console.error('💥 [TonPayment] Connection error:', err);
        error.value = err.message || 'Ошибка подключения кошелька';
    }
};

const sendTransaction = async (toAddress: string, amount: number, comment: string) => {
  try {
    // Если кошелек подключен через TonConnect
    if (walletStore.isConnected && walletStore.walletAddress) {
      // Используем TonConnect для отправки
      const transaction = {
        validUntil: Date.now() + 1000000,
        messages: [
          {
            address: toAddress,
            amount: Math.floor(amount * 1e9).toString(),
            payload: comment ? btoa(comment) : undefined
          }
        ]
      };
      
      // ✅ Отправляем через сервис
      const connector = tonConnectService.getConnector();
      if (connector && connector.sendTransaction) {
        return await connector.sendTransaction(transaction);
      }
    }
    
    // Fallback: открываем deep link
    const deepLink = createTelegramPaymentLink(amount);
    openTelegramLink(deepLink);
    
    return { 
      boc: `pending_${Date.now()}`,
      status: 'pending'
    };
    
  } catch (error) {
    console.error('Transaction error:', error);
    throw error;
  }
};

const disconnectWallet = () => {
    walletStore.disconnect()
    amount.value = ''
    error.value = ''
    successMessage.value = ''
}

const deposit = () => {
    if (!isValidAmount.value) {
        error.value = 'Неверная сумма'
        return
    }
    showConfirmation.value = true
}

const confirmDeposit = async () => {
  showConfirmation.value = false;
  isProcessing.value = true;
  error.value = '';
  successMessage.value = '';

  try {
    const depositAmount = parseFloat(amount.value);
    
    // ✅ Используем новый метод sendTransaction
    const result = await sendTransaction(
      appWalletAddress.value,
      depositAmount,
      `deposit:${userStore.user?.telegram_id}`
    );

    const response = await api.post('/wallet/deposit', {
      amount: depositAmount,
      tx_hash: result.boc,
      from_address: walletStore.walletAddress,
      status: result.status || 'pending'
    });

    if (response.data.status === 'success') {
      successMessage.value = isTelegramWebApp() 
        ? 'Откройте кошелек для подтверждения перевода' 
        : 'Транзакция отправлена! Ожидайте подтверждения.';
      
      setTimeout(async () => {
        await userStore.fetchBalance();
        await walletStore.updateBalance();
      }, 3000);
      
      if (!isTelegramWebApp()) {
        setTimeout(() => {
          router.back();
        }, 2000);
      }
    }

  } catch (err: any) {
    console.error('Deposit error:', err);
    error.value = err.response?.data?.detail || 
                 err.message || 
                 'Ошибка при отправке транзакции';
  } finally {
    isProcessing.value = false;
  }
};

const handleWalletReturn = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const hashParams = new URLSearchParams(window.location.hash.slice(1));
  
  const hasTonConnect = urlParams.has('tonconnect') || 
                       hashParams.has('tonconnect') ||
                       urlParams.has('startattach') || 
                       hashParams.has('startattach');
  
  if (hasTonConnect) {
    console.log('🔄 Handling wallet return...');
    
    // Очищаем URL
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
    
    // ✅ Используем сервис для обработки возврата
    setTimeout(async () => {
      try {
        await tonConnectService.handleReturnFromWallet();
        await walletStore.checkConnection();
      } catch (error) {
        console.error('Error handling wallet return:', error);
      }
    }, 1000);
  }
};

onMounted(() => {
  handleWalletReturn();
  walletStore.updateBalance().catch(console.error);
  
  // ✅ Слушаем изменения статуса кошелька
  const unsubscribe = walletStore.$subscribe((mutation, state) => {
    if (mutation.events?.has('isConnected') && state.isConnected) {
      console.log('✅ Wallet connected, updating balance');
      walletStore.updateBalance().catch(console.error);
    }
  });
  
  transactionWatcher.startWatching();
  
  onUnmounted(() => {
    unsubscribe();
    transactionWatcher.stopWatching();
  });
});


</script>


<style scoped>
.ton-payment {
    padding: 20px;
    max-width: 400px;
    margin: 0 auto;
}

.connect-section, .payment-section {
    text-align: center;
}

.connect-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 15px;
}

.ton-logo {
    width: 32px;
    height: 32px;
}

.wallet-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.wallet-header, .balance-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.wallet-address {
    font-family: monospace;
    font-size: 12px;
}

.balance-amount {
    font-weight: bold;
    color: #28a745;
}

.two-buttons-container {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn.primary {
    background: #6c757d;
    color: white;
}

.btn.secondary {
    background: #007bff;
    color: white;
}

.btn.connect-btn {
    background: #28a745;
    color: white;
    padding: 15px 25px;
    font-size: 16px;
}

.disconnect-btn {
    margin-top: 20px;
    background: none;
    border: 1px solid #dc3545;
    color: #dc3545;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    width: 100%;
}

.disconnect-btn:hover {
    background: #dc3545;
    color: white;
}

/* Стили для модального окна */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.confirmation-modal {
    background: white;
    padding: 20px;
    border-radius: 12px;
    max-width: 400px;
    width: 90%;
    text-align: center;
}

.wallet-address-confirm {
    word-break: break-all;
    font-family: monospace;
    background: #f5f5f5;
    padding: 10px;
    border-radius: 6px;
    margin: 10px 0;
    font-size: 12px;
}

.modal-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn.cancel {
    background: #6c757d;
    color: white;
}

.btn.confirm {
    background: #28a745;
    color: white;
}

/* Уведомления */
.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 10px;
    border-radius: 6px;
    margin-top: 15px;
    border: 1px solid #f5c6cb;
}

.success-message {
    background: #d4edda;
    color: #155724;
    padding: 10px;
    border-radius: 6px;
    margin-top: 15px;
    border: 1px solid #c3e6cb;
}
</style>