<template>
  <div class="top-all-container">
    <div class="history-header">
      <h4 style="color: #F0F0F080;">Всего ставок:</h4>
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
        <div class="bet-number">{{ bet.bet_number }}</div>
        
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
        
        <div class="bet-time">{{ formatTime(bet.created_at) }}</div>
      </div>
      
      <!-- Остальной код без изменений -->
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

/* ОСНОВНОЙ СТИЛЬ ПАНЕЛЕК */
.bet-item {
  display: grid;
  grid-template-columns: 45px 1fr 70px 90px 55px;
  gap: 10px;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 6px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
  border: none; /* Убираем бордер */
  border: 1px solid #6C4DB1;
}

/* СТИЛЬ ДЛЯ ВЫИГРЫШНОЙ СТАВКИ */
.bet-item.won {
  background: #534081B2; /* Фиолетовый с прозрачностью */
}

/* СТИЛЬ ДЛЯ ПРОИГРЫШНОЙ СТАВКИ */
.bet-item.lost {
  background: #1D1131; /* Темно-фиолетовый */
}

/* СТИЛЬ ДЛЯ СТАВКИ В ПРОЦЕССЕ */


/* НОМЕР СТАВКИ */
.bet-number {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  text-align: center;
}

/* СЕКЦИЯ С СУММОЙ СТАВКИ */
.bet-amount-section {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-start;
}

.bet-amount {
  font-weight: 600;
  color: #ffffff;
  font-size: 13px;
}

/* ПАНЕЛЬКА КОЭФФИЦИЕНТА */
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

/* СЕКЦИЯ ВЫИГРЫША */
.bet-profit-section {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

.bet-profit {
  font-weight: 600;
  font-size: 13px;
}

/* ИКОНКА ВАЛЮТЫ */
.currency-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
  filter: brightness(0.9);
}

/* ВРЕМЯ */
.bet-time {
  text-align: center;
  font-size: 11px;
  color: #a0a0b0;
  opacity: 0.8;
}

/* АДАПТИВНОСТЬ */
@media (max-width: 768px) {
  .bet-item {
    grid-template-columns: 40px 1fr 65px 80px 50px;
    gap: 8px;
    padding: 8px 10px;
    font-size: 0.9em;
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
  .bet-item {
    grid-template-columns: 35px 1fr 60px 70px 45px;
    gap: 6px;
    padding: 6px 8px;
    font-size: 0.8em;
  }
  
  .top-all-container {
    padding: 12px;
    margin: 12px 0;
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
.bet-item:hover {
  transform: translateX(2px);
  background: rgba(255, 255, 255, 0.08);
}

.bet-item.won:hover {
  background: #5a4899B2;
}

.bet-item.lost:hover {
  background: #24153F;
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
</style>