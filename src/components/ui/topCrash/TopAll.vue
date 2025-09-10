<template>
  <div class="top-all-container">
    <div class="history-header">
      <h4 style="color: #F0F0F080;">Всего ставок: {{ filteredBetHistory.length }}</h4>
      <button @click="refreshHistory" class="refresh-btn">
        <img src="@/assets/images/refresh-small.svg" alt="Refresh">
      </button>
    </div>
    
    <div class="bets-list-vertical" ref="betsList">
      <div 
        v-for="bet in filteredBetHistory" 
        :key="bet.id"
        class="bet-item-vertical"
        :class="{ 
          won: bet.status === 'won', 
          lost: bet.status === 'lost'
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
            profit: bet.status === 'won', 
            loss: bet.status === 'lost' 
          }">
            <span class="bet-profit">{{ formatProfit(bet) }}</span>
            <img src="@/assets/images/coin.svg" class="currency-icon" alt="stars">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useBetHistory } from '@/composables/useBetHistory'
import { api } from '@/services/api'
import { useWebSocket } from '@/composables/useWebSocket'

const userStore = useUserStore()
const { betHistory, loading, addNewBet, setBetHistory } = useBetHistory()
const error = ref<string | null>(null)
const betsList = ref<HTMLElement | null>(null)

// Фильтруем историю ставок, исключая pending
const filteredBetHistory = computed(() => {
  return betHistory.value.filter(bet => bet.status !== 'pending')
})

// Подключаем WebSocket и передаем callback функции
const { connectToCrashGame } = useWebSocket({
  onNewBet: addNewBet,
  onBetHistory: setBetHistory
})

const formatAmount = (amount: number) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatProfit = (bet: any) => {
  if (bet.status === 'won') {
    // Рассчитываем выигрыш: ставка × коэффициент, округляем до целого
    const winAmount = Math.round(bet.bet_amount * bet.crash_coefficient);
    return `+${formatAmount(winAmount)}`;
  } else if (bet.status === 'lost') {
    return `-${formatAmount(bet.bet_amount)}`;
  } else {
    // Для других статусов (на всякий случай)
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
  border-radius: 12px;
  padding: 12px;
  margin: 12px 0;
  max-height: 380px;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
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
  font-size: 14px;
  margin: 0;
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
  width: 14px;
  height: 14px;
  filter: brightness(0.8);
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
  display: flex;
  flex-direction: column;
  padding: 10px;
  margin-bottom: 6px;
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

.bet-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.bet-number {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
}

.bet-time {
  font-size: 10px;
  color: #a0a0b0;
  opacity: 0.8;
}

.bet-details-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: nowrap;
  width: 100%;
}

.bet-amount-section {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.bet-amount {
  font-weight: 600;
  color: #ffffff;
  font-size: 12px;
}

.bet-multiplier-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  padding: 4px 6px;
  text-align: center;
  font-weight: 600;
  color: #ffffff;
  font-size: 11px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  margin: 0 4px;
}

.bet-profit-section {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.bet-profit-section.profit {
  color: #4caf50;
}

.bet-profit-section.loss {
  color: #f44336;
}

.bet-profit {
  font-weight: 600;
  font-size: 12px;
}

.currency-icon {
  width: 12px;
  height: 12px;
  object-fit: contain;
  filter: brightness(0.9);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .top-all-container {
    padding: 10px;
    margin: 10px 0;
    max-height: 340px;
  }
  
  .bet-item-vertical {
    padding: 8px;
  }
  
  .bet-number {
    font-size: 11px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 11px;
  }
  
  .bet-multiplier-panel {
    font-size: 10px;
    padding: 3px 5px;
  }
  
  .currency-icon {
    width: 11px;
    height: 11px;
  }
  
  .bet-time {
    font-size: 9px;
  }
}

@media (max-width: 480px) {
  .top-all-container {
    padding: 8px;
    margin: 8px 0;
    max-height: 300px;
  }
  
  .bet-item-vertical {
    padding: 6px;
    margin-bottom: 4px;
  }
  
  .bet-number {
    font-size: 10px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 10px;
  }
  
  .currency-icon {
    width: 10px;
    height: 10px;
  }
  
  .bet-time {
    font-size: 9px;
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
}
</style>