<template>
  <div class="top-all-container">
    <div class="history-header">
      <h3>История ставок</h3>
      <button @click="refreshHistory" class="refresh-btn">
        <img src="@/assets/images/refresh-small.svg" alt="Refresh">
      </button>
    </div>
    
    <div class="bets-list" ref="betsList">
      <div 
        v-for="bet in betHistory" 
        :key="bet.id"
        class="bet-item"
        :class="{ 
          won: bet.status === 'won', 
          lost: bet.status === 'lost',
          pending: bet.status === 'pending'
        }"
      >
        <div class="bet-number">#{{ bet.bet_number }}</div>
        <div class="bet-amount">{{ formatAmount(bet.bet_amount) }} stars</div>
        <div class="bet-multiplier">
          {{ bet.crash_coefficient ? bet.crash_coefficient.toFixed(2) + 'x' : '-' }}
        </div>
        <div class="bet-profit" :class="{ 
          profit: bet.win_amount > 0, 
          loss: bet.win_amount <= 0 
        }">
          {{ formatProfit(bet.win_amount) }}
        </div>
        <div class="bet-time">{{ formatTime(bet.created_at) }}</div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="loader"></div>
        Загрузка истории...
      </div>
      
      <div v-if="!loading && betHistory.length === 0" class="empty-state">
        <img src="@/assets/images/gameicon.svg" alt="No bets">
        <p>Ставок еще не было</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useBetHistory } from '@/composables/useBetHistory'
import { api } from '@/services/api'
import { useWebSocket } from '@/composables/useWebSocket'

const userStore = useUserStore()
const { betHistory, loading, addNewBet, setBetHistory } = useBetHistory()
const error = ref<string | null>(null)
const betsList = ref<HTMLElement | null>(null)

// Подключаем WebSocket и передаем callback функции
const { connectToCrashGame } = useWebSocket({
  onNewBet: addNewBet,
  onBetHistory: setBetHistory
})

const formatAmount = (amount: number) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatProfit = (profit: number) => {
  if (profit > 0) {
    return `+${formatAmount(profit)}`
  }
  return formatAmount(profit)
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadBetHistory = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get('/api/crash/bet-history', {
      params: { limit: 100 }
    })
    
    setBetHistory(response.data.bets)
  } catch (err: any) {
    console.error('Failed to load bet history:', err)
    error.value = err.response?.data?.detail || 'Ошибка загрузки истории'
  } finally {
    loading.value = false
  }
}

const refreshHistory = () => {
  loadBetHistory()
}

const scrollToTop = () => {
  nextTick(() => {
    if (betsList.value) {
      betsList.value.scrollTop = 0
    }
  })
}

onMounted(async () => {
  await loadBetHistory()
  await connectToCrashGame() // Подключаемся к WebSocket каналу краш-игры
  
  // Обновляем историю каждые 30 секунд
  setInterval(loadBetHistory, 30000)
})
</script>

<style scoped>
/* Стили остаются такими же как в предыдущем примере */
.top-all-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 16px;
  margin: 16px 0;
  max-height: 400px;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1em;
  font-weight: 600;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.refresh-btn img {
  width: 16px;
  height: 16px;
  filter: brightness(0.8);
}

.bets-list {
  max-height: 320px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.bets-list::-webkit-scrollbar {
  width: 4px;
}

.bets-list::-webkit-scrollbar-track {
  background: transparent;
}

.bets-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.bet-item {
  display: grid;
  grid-template-columns: 50px 1fr 80px 100px 60px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.bet-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
}

.bet-item.won {
  border-left: 4px solid #00ff88;
}

.bet-item.lost {
  border-left: 4px solid #ff6b6b;
}

.bet-item.pending {
  border-left: 4px solid #f59e0b;
}

.bet-number {
  font-size: 0.8em;
  color: #a0a0b0;
  text-align: center;
}

.bet-amount {
  font-weight: 600;
  color: #ffffff;
}

.bet-multiplier {
  text-align: center;
  font-weight: 600;
  color: #6366f1;
}

.bet-profit {
  text-align: right;
  font-weight: 600;
}

.bet-profit.profit {
  color: #00ff88;
}

.bet-profit.loss {
  color: #ff6b6b;
}

.bet-time {
  text-align: center;
  font-size: 0.8em;
  color: #a0a0b0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px;
  color: #a0a0b0;
}

.loader {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
  color: #a0a0b0;
  text-align: center;
}

.empty-state img {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.9em;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  .bet-item {
    grid-template-columns: 40px 1fr 70px 80px 50px;
    gap: 8px;
    padding: 8px;
    font-size: 0.9em;
  }
  
  .bet-number {
    font-size: 0.7em;
  }
  
  .bet-time {
    font-size: 0.7em;
  }
}

@media (max-width: 480px) {
  .bet-item {
    grid-template-columns: 30px 1fr 60px 70px 40px;
    gap: 6px;
    padding: 6px;
    font-size: 0.8em;
  }
  
  .top-all-container {
    padding: 12px;
    margin: 12px 0;
  }
}
</style>