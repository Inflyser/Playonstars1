<template>
  <div class="stars-payment">
    <InputPanel
      v-model="amount"
      prefix-text="STARS"
      :placeholder="t('balance_sum_star')"
      max-value="5000"
      icon-type="stars"
    />

    <p style="color: #6A717B; font-size: 13px; margin: -10px 10px 15px 20px;">
      {{ t('balance_sum_star1') }}
    </p>
    
    <div class="two-buttons-container">
      <button class="btn primary" @click="$router.back()">{{ t('balance_but1') }}</button>
      <button 
        class="btn secondary" 
        @click="initiateTelegramPayment"
        :disabled="!isValidAmount || isProcessing"
      >
        <span v-if="isProcessing">Обработка...</span>
        <span v-else>{{ t('balance_sum_star2') }}</span>
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
import { useI18n } from 'vue-i18n'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import InputPanel from '@/components/layout/InputPanel.vue'
import { api } from '@/services/api'
import { useUserStore } from '@/stores/useUserStore'
import { isInvoiceSupported, openInvoice, retrieveLaunchParams } from '@telegram-apps/sdk'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

const amount = ref('')
const isProcessing = ref(false)
const error = ref('')
const successMessage = ref('')
const telegramUser = ref<any>(null)

// ✅ Получаем данные пользователя Telegram
onMounted(() => {
  try {
    const launchParams = retrieveLaunchParams()
    telegramUser.value = launchParams.user
    console.log('Telegram user:', telegramUser.value)
  } catch (e) {
    console.error('Failed to get Telegram user:', e)
    error.value = 'Не удалось получить данные пользователя'
  }
})

const isValidAmount = computed(() => {
  const numAmount = parseFloat(amount.value || '0')
  return numAmount >= 10 && numAmount <= 5000
})

const initiateTelegramPayment = async () => {
  if (!isValidAmount.value) {
    error.value = 'Неверная сумма. Минимум 10 STARS, максимум 5000 STARS'
    return
  }

  if (!telegramUser.value?.id) {
    error.value = 'Не удалось определить пользователя'
    return
  }

  isProcessing.value = true
  error.value = ''
  successMessage.value = ''

  try {
    const starsAmount = parseFloat(amount.value)
    
    // ✅ Правильный запрос с user_id
    const invoiceResponse = await api.post('/api/stars/create-invoice', {
      amount: starsAmount,
      telegram_id: telegramUser.value.id  // ✅ Добавляем telegram_id
    })

    console.log('Invoice response:', invoiceResponse.data)

    if (invoiceResponse.data.status === 'success') {
      // ✅ Проверяем поддержку платежей
      if (isInvoiceSupported()) {
        const result = await openInvoice(invoiceResponse.data.invoice_link)
        handlePaymentStatus(result.status, starsAmount)
      } else {
        // Fallback для WebApp
        if (window.Telegram?.WebApp?.openInvoice) {
          window.Telegram.WebApp.openInvoice(
            invoiceResponse.data.invoice_link,
            (status: string) => {
              handlePaymentStatus(status as 'paid' | 'failed' | 'cancelled' | 'pending', starsAmount)
            }
          )
        } else {
          throw new Error('Оплата через Telegram недоступна в вашем клиенте')
        }
      }
    } else {
      throw new Error(invoiceResponse.data.detail || 'Ошибка создания инвойса')
    }

  } catch (err: any) {
    console.error('Payment error:', err)
    error.value = err.response?.data?.detail || err.message || 'Ошибка при создании платежа'
  } finally {
    isProcessing.value = false
  }
}

const handlePaymentStatus = (status: 'paid' | 'failed' | 'cancelled' | 'pending', starsAmount: number) => {
  console.log('Payment status:', status)
  
  if (status === 'paid') {
    userStore.fetchBalance().then(() => {
      successMessage.value = `✅ Успешно пополнено ${starsAmount} STARS!`
      setTimeout(() => router.back(), 2000)
    })
  } else if (status === 'failed') {
    error.value = 'Оплата не удалась. Попробуйте снова.'
  } else if (status === 'cancelled') {
    console.log('Пользователь отменил оплату')
    error.value = 'Оплата отменена.'
  }
}
</script>


<style scoped>
.stars-payment {
  padding: 20px;
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
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid #2A2642;
}

.secondary:not(:disabled):hover {
  background: linear-gradient(135deg, #0088CC, #006699);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 136, 204, 0.3);
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 8px;
  margin: 15px;
  border: 1px solid #f5c6cb;
  font-size: 14px;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 8px;
  margin: 15px;
  border: 1px solid #c3e6cb;
  font-size: 14px;
}
</style>