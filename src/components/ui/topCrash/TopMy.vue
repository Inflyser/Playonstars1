<template>
  <div class="top-all-container">
    <div class="history-header">
      <h4 style="color: #F0F0F080;">Мои ставки: {{ myBets.length }}</h4>
      <button @click="refreshHistory" class="refresh-btn">
        <img src="@/assets/images/reload.svg" alt="Refresh">
      </button>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <span>Загрузка...</span>
    </div>
    
    <div v-else-if="error" class="error-container">
      <span>{{ error }}</span>
      <button @click="refreshHistory" class="retry-btn">Повторить</button>
    </div>
    
    <div v-else-if="myBets.length === 0" class="empty-container">
      <img src="@/assets/images/empty-bets.svg" alt="No bets" class="empty-icon">
      <span>У вас еще нет ставок</span>
    </div>
    
    <div v-else class="bets-list-vertical" ref="betsList">
      <div 
        v-for="bet in myBets" 
        :key="bet.id"
        class="bet-item-vertical"
        :class="{ 
          won: bet.status === 'won', 
          lost: bet.status === 'lost',
          pending: bet.status === 'pending'
        }"
      >
        <div class="bet-single-row">
          <div class="bet-number-time">
            <div class="bet-number">#{{ bet.bet_number }}</div>
            <div class="bet-time">{{ formatTime(bet.created_at) }}</div>
          </div>
          
          <div class="bet-amount-section">
            <span class="bet-amount">{{ formatAmount(bet.bet_amount) }}</span>
            <img src="@/assets/images/coin.svg" class="currency-icon" alt="stars">
          </div>
          
          <div class="bet-multiplier-panel" :class="getMultiplierClass(bet)">
            {{ bet.crash_coefficient ? bet.crash_coefficient.toFixed(2) + 'x' : 'x' }}
          </div>
          
          <div class="bet-profit-section">
            <span class="bet-profit">{{ formatProfit(bet) }}</span>
            <span v-if="bet.status !== 'lost'" class="currency-icon-container">
              <img src="@/assets/images/coin.svg" class="currency-icon" alt="stars">
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { api } from '@/services/api'
import { useWebSocket } from '@/composables/useWebSocket'

const userStore = useUserStore()
const loading = ref(false)
const error = ref<string | null>(null)
const betsList = ref<HTMLElement | null>(null)
const myBets = ref<any[]>([])

// Вычисляемое свойство для отфильтрованных ставок пользователя
const filteredMyBets = computed(() => {
  return myBets.value.slice(0, 50) // Ограничиваем количество отображаемых ставок
})

// Функция для определения класса множителя
const getMultiplierClass = (bet: any) => {
  if (bet.status === 'lost' || bet.status === 'pending') {
    return 'multiplier-low';
  }
  
  if (!bet.crash_coefficient) {
    return 'multiplier-low';
  }
  
  if (bet.crash_coefficient < 2) {
    return 'multiplier-low';
  } else if (bet.crash_coefficient >= 2 && bet.crash_coefficient < 7) {
    return 'multiplier-medium';
  } else {
    return 'multiplier-high';
  }
}

// Обработчик новых ставок из WebSocket
const handleNewBet = (newBet: any) => {
  // Проверяем, принадлежит ли ставка текущему пользователю
  if (newBet.user_id === userStore.user?.id || newBet.telegram_id === userStore.user?.telegram_id) {
    // Добавляем ставку в начало списка
    myBets.value.unshift(newBet);
    
    // Ограничиваем количество ставок (например, последние 50)
    if (myBets.value.length > 50) {
      myBets.value = myBets.value.slice(0, 50);
    }
  }
}

// Подключаем WebSocket
const { connectToCrashGame } = useWebSocket({
  onNewBet: handleNewBet
})

const formatAmount = (amount: number) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatProfit = (bet: any) => {
  if (bet.status === 'won') {
    const winAmount = Math.round(bet.bet_amount * bet.crash_coefficient);
    return formatAmount(winAmount);
  } else if (bet.status === 'lost') {
    return '—';
  } else {
    return formatAmount(0);
  }
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadMyBetHistory = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get('/api/crash/my-bets', {
      params: { 
        limit: 50,
        user_id: userStore.user?.id
      }
    })
    
    myBets.value = response.data.bets || []
  } catch (err: any) {
    console.error('Failed to load my bet history:', err)
    error.value = err.response?.data?.detail || 'Ошибка загрузки истории ставок'
  } finally {
    loading.value = false
  }
}

const refreshHistory = () => {
  loadMyBetHistory()
}

const scrollToTop = () => {
  nextTick(() => {
    if (betsList.value) {
      betsList.value.scrollTop = 0
    }
  })
}

onMounted(async () => {
  if (userStore.user) {
    await loadMyBetHistory()
    await connectToCrashGame()
    
    // Обновляем историю каждые 30 секунд
    setInterval(loadMyBetHistory, 30000)
  } else {
    error.value = 'Требуется авторизация'
  }
})
</script>

<style scoped>
.top-all-container {
  border-radius: 12px;
  padding: 12px;
  margin: 12px 0;
  max-height: 380px;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.03);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-header h4 {
  font-size: 16px;
  margin: 0;
  color: #F0F0F0;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.refresh-btn img {
  width: 16px;
  height: 16px;
  filter: brightness(0.8);
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #a0a0b0;
  text-align: center;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #6C4DB1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background: rgba(108, 77, 177, 0.3);
  border: 1px solid #6C4DB1;
  border-radius: 6px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: rgba(108, 77, 177, 0.5);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.bets-list-vertical {
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.bets-list-vertical::-webkit-scrollbar {
  width: 4px;
}

.bets-list-vertical::-webkit-scrollbar-track {
  background: transparent;
}

.bets-list-vertical::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.bet-item-vertical {
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
  border: 1px solid #6C4DB1;
  box-sizing: border-box;
  width: 100%;
}

.bet-item-vertical.won {
  background: #534081B2;
}

.bet-item-vertical.lost {
  background: #1D1131;
}

.bet-item-vertical.pending {
  background: rgba(255, 255, 255, 0.08);
}

.bet-single-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}

.bet-number-time {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 55px;
  flex-shrink: 0;
}

.bet-number {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.2;
}

.bet-time {
  font-size: 11px;
  color: #a0a0b0;
  opacity: 0.8;
  line-height: 1.2;
  margin-top: 2px;
}

.bet-amount-section {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  min-width: 65px;
  justify-content: flex-end;
}

.bet-amount {
  font-weight: 600;
  color: #ffffff;
  font-size: 13px;
  white-space: nowrap;
}

.bet-multiplier-panel {
  border-radius: 5px;
  padding: 5px 7px;
  text-align: center;
  font-weight: 600;
  color: #ffffff;
  font-size: 13px;
  border: 1px solid;
  flex-shrink: 0;
  min-width: 50px;
}

.bet-multiplier-panel.multiplier-low {
  border-color: #4B7ED0;
  background: #355391;
}

.bet-multiplier-panel.multiplier-medium {
  border-color: #764BD0;
  background: #5A3A9E;
}

.bet-multiplier-panel.multiplier-high {
  border-color: #83CE38;
  background: #67A32B;
}

.bet-profit-section {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  min-width: 65px;
  justify-content: flex-end;
}

.bet-profit {
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  color: #ffffff;
}

.currency-icon {
  width: 13px;
  height: 13px;
  object-fit: contain;
  filter: brightness(0.9);
  flex-shrink: 0;
}

.currency-icon-container {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .top-all-container {
    padding: 10px;
    margin: 10px 0;
    max-height: 340px;
  }
  
  .bet-item-vertical {
    padding: 8px 10px;
  }
  
  .loading-container,
  .error-container,
  .empty-container {
    padding: 30px 15px;
  }
}

@media (max-width: 480px) {
  .top-all-container {
    padding: 8px;
    margin: 8px 0;
    max-height: 300px;
  }
  
  .bet-item-vertical {
    padding: 6px 8px;
    margin-bottom: 6px;
  }
}

.bet-item-vertical:hover {
  transform: translateX(2px);
  background: rgba(255, 255, 255, 0.08);
}

.bet-item-vertical.won:hover {
  background: #5a4899B2;
}

.bet-item-vertical.lost:hover {
  background: #24153F;
  border: 1px solid #25213C;
}

.bet-item-vertical.pending:hover {
  background: rgba(255, 255, 255, 0.12);
}
</style>