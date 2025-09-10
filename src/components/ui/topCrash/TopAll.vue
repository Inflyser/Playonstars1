<template>
  <div class="top-all-container">
    <div class="history-header">
      <h4 style="color: #F0F0F080;">Всего ставок:</h4>
      <button @click="refreshHistory" class="refresh-btn">
        <img src="@/assets/images/refresh-small.svg" alt="Refresh">
      </button>
    </div>
    
    <div class="bets-list-vertical" ref="betsList">
      <div 
        v-for="bet in betHistory" 
        :key="bet.id"
        class="bet-item-vertical"
        :class="{ 
          won: bet.status === 'won', 
          lost: bet.status === 'lost',
          pending: bet.status === 'pending'
        }"
      >
        <div class="bet-info-row">
          <div class="bet-number">{{ bet.bet_number }}</div>
          <div class="bet-time">{{ formatTime(bet.created_at) }}</div>
        </div>
        
        <div class="bet-details-row">
          <div class="bet-amount-section">
            <span class="bet-amount">{{ formatAmount(bet.bet_amount) }}</span>
            <img src="@/assets/images/coin.svg" class="currency-icon" alt="stars">
          </div>
          
          <div class="bet-multiplier-panel">
            {{ bet.crash_coefficient ? bet.crash_coefficient.toFixed(2) + 'x' : 'x' }}
          </div>
          
          <div class="bet-profit-section" :class="{ 
            profit: bet.win_amount > 0, 
            loss: bet.win_amount <= 0 
          }">
            <span class="bet-profit">{{ formatProfit(bet.win_amount) }}</span>
            <img src="@/assets/images/coin.svg" class="currency-icon" alt="stars">
          </div>
        </div>
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
.top-all-container {
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

.bets-list-vertical {
  max-height: 320px;
  overflow-y: auto;
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

/* ВЕРТИКАЛЬНЫЙ СТИЛЬ ДЛЯ СТАВОК */
.bet-item-vertical {
  display: flex;
  flex-direction: column;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
  border: 1px solid #6C4DB1;
}

.bet-item-vertical.won {
  background: #534081B2;
}

.bet-item-vertical.lost {
  background: #1D1131;
}

.bet-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.bet-number {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.bet-time {
  font-size: 11px;
  color: #a0a0b0;
  opacity: 0.8;
}

.bet-details-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bet-amount-section {
  display: flex;
  align-items: center;
  gap: 4px;
}

.bet-amount {
  font-weight: 600;
  color: #ffffff;
  font-size: 13px;
}

.bet-multiplier-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 5px 8px;
  text-align: center;
  font-weight: 600;
  color: #ffffff;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.bet-profit-section {
  display: flex;
  align-items: center;
  gap: 4px;
}

.bet-profit {
  font-weight: 600;
  font-size: 13px;
}

.currency-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
  filter: brightness(0.9);
}

/* АДАПТИВНОСТЬ */
@media (max-width: 768px) {
  .bet-item-vertical {
    padding: 10px;
  }
  
  .bet-number {
    font-size: 13px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 12px;
  }
  
  .bet-multiplier-panel {
    font-size: 11px;
    padding: 4px 6px;
  }
  
  .currency-icon {
    width: 12px;
    height: 12px;
  }
  
  .bet-time {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .top-all-container {
    padding: 12px;
    margin: 12px 0;
  }
  
  .bet-item-vertical {
    padding: 8px;
  }
  
  .bet-number {
    font-size: 12px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 11px;
  }
  
  .currency-icon {
    width: 11px;
    height: 11px;
  }
}

/* Анимации */
.bet-item-vertical:hover {
  transform: translateX(2px);
  background: rgba(255, 255, 255, 0.08);
}

.bet-item-vertical.won:hover {
  background: #5a4899B2;
}

.bet-item-vertical.lost:hover {
  background: #24153F;
}
</style>