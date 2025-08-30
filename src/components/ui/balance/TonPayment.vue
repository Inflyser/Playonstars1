<template>
    <div class="ton-payment">
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
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import InputPanel from '@/components/layout/InputPanel.vue'
import { useWalletStore } from '@/stores/useWalletStore'

const router = useRouter()
const walletStore = useWalletStore()

// Используем storeToRefs для реактивности
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

// Инициализация при монтировании
onMounted(async () => {
    await walletStore.init()
})

// Вычисляемые свойства
const maxAmount = computed(() => tonBalance.value.toString())
const isValidAmount = computed(() => {
    const numAmount = parseFloat(amount.value)
    return numAmount >= 0.1 && numAmount <= tonBalance.value
})

// Методы
const connectWallet = async () => {
    try {
        error.value = ''
        await walletStore.connect()
    } catch (err) {
        error.value = 'Ошибка подключения кошелька'
        console.error('Connection error:', err)
    }
}

const disconnectWallet = () => {
    walletStore.disconnect()
    amount.value = ''
    error.value = ''
    successMessage.value = ''
}

const deposit = async () => {
    if (!isValidAmount.value) return

    isProcessing.value = true
    error.value = ''
    successMessage.value = ''

    try {
        const depositAmount = parseFloat(amount.value)
        const result = await walletStore.deposit(depositAmount)
        
        successMessage.value = `Успешно пополнено ${depositAmount} TON!`
        amount.value = ''
        
        // Обновляем баланс после успешного депозита
        await walletStore.updateBalance()
        
        // Можно добавить автоматический возврат через несколько секунд
        setTimeout(() => {
            router.back()
        }, 2000)
        
    } catch (err: any) {
        error.value = err.response?.data?.detail || 'Ошибка при пополнении'
        console.error('Deposit error:', err)
    } finally {
        isProcessing.value = false
    }
}
</script>

<style scoped>
.ton-payment {
    padding: 20px;
    min-height: 100vh;
    background: var(--tg-theme-bg-color);
}

.connect-section {
    text-align: center;
    padding: 40px 20px;
}

.connect-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 16px;
}

.ton-logo {
    width: 32px;
    height: 32px;
}

.connect-section h3 {
    color: var(--tg-theme-text-color);
    margin: 0;
    font-size: 18px;
}

.connect-section p {
    color: var(--tg-theme-hint-color);
    margin-bottom: 24px;
    font-size: 14px;
}

.connect-btn {
    background: linear-gradient(135deg, #0088CC, #0066AA);
    color: white;
    border: none;
    padding: 16px 32px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    width: 100%;
}

.payment-section {
    padding-top: 20px;
}

.wallet-info {
    background: var(--tg-theme-secondary-bg-color);
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.wallet-header, .balance-info {
    display: flex;
    justify-content: between;
    margin-bottom: 8px;
}

.wallet-header span:first-child,
.balance-info span:first-child {
    color: var(--tg-theme-hint-color);
    flex: 1;
}

.wallet-address {
    color: var(--tg-theme-text-color);
    font-family: monospace;
}

.balance-amount {
    color: var(--tg-theme-button-color);
    font-weight: 600;
}

.two-buttons-container {
    display: flex;
    gap: 12px;
    padding: 0 15px 15px 15px;
}

.btn {
    flex: 1;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.primary {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.secondary {
    background: linear-gradient(135deg, #00A6FC, #0088CC);
    color: white;
}

.secondary:disabled {
    background: rgba(0, 166, 252, 0.5);
}

.disconnect-btn {
    width: 100%;
    background: none;
    border: 1px solid var(--tg-theme-destructive-bg-color);
    color: var(--tg-theme-destructive-text-color);
    padding: 12px;
    border-radius: 8px;
    margin-top: 16px;
    cursor: pointer;
}

.error-message {
    color: var(--tg-theme-destructive-text-color);
    background: var(--tg-theme-destructive-bg-color);
    padding: 12px;
    border-radius: 8px;
    margin: 16px 0;
    text-align: center;
}

.success-message {
    color: var(--tg-theme-button-color);
    background: rgba(0, 136, 204, 0.1);
    padding: 12px;
    border-radius: 8px;
    margin: 16px 0;
    text-align: center;
    border: 1px solid var(--tg-theme-button-color);
}
</style>