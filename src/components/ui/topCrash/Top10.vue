<template>
  <div class="top-all-container">
    <div class="history-header">
      <h4 style="color: #F0F0F080;">{{ t('all_stavka') }}: {{ recentBets.length }}</h4>
      <button @click="refreshHistory" class="refresh-btn">
        <img src="@/assets/images/reload.svg" alt="Refresh">
      </button>
    </div>
    
    <div class="bets-list-vertical" ref="betsList">
      <div 
        v-for="bet in recentBets" 
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
            <div class="bet-number">{{ bet.bet_number }}</div>
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

import { ref, onMounted, nextTick, computed } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useBetHistory } from '@/composables/useBetHistory'
import { api } from '@/services/api'
import { useWebSocket } from '@/composables/useWebSocket'

const userStore = useUserStore()
const { betHistory, loading, addNewBet, setBetHistory } = useBetHistory()
const error = ref<string | null>(null)
const betsList = ref<HTMLElement | null>(null)

// Вычисляемое свойство для последних 10 ставок
const recentBets = computed(() => {
  return betHistory.value.slice(0, 10) // Берем только первые 10 элементов
})

// Функция для определения класса множителя
const getMultiplierClass = (bet: any) => {
  if (bet.status === 'lost' || bet.status === 'pending') {
    return 'multiplier-low'; // Для проигранных и pending ставок - синий
  }
  
  if (!bet.crash_coefficient) {
    return 'multiplier-low'; // По умолчанию синий
  }
  
  if (bet.crash_coefficient < 2) {
    return 'multiplier-low'; // Меньше 2 - синий
  } else if (bet.crash_coefficient >= 2 && bet.crash_coefficient < 7) {
    return 'multiplier-medium'; // От 2 до 6.99 - фиолетовый
  } else {
    return 'multiplier-high'; // 7 и больше - зеленый
  }
}

// Подключаем WebSocket и передаем callback функции
const { connectToCrashGame } = useWebSocket({
  onNewBet: (newBet) => {
    // Добавляем новую ставку и ограничиваем историю до 10 элементов
    addNewBet(newBet);
    
    // Если история становится больше 10 элементов, обрезаем ее
    if (betHistory.value.length > 10) {
      setBetHistory(betHistory.value.slice(0, 10));
    }
  },
  onBetHistory: (history) => {
    // При получении истории берем только последние 10 ставок
    setBetHistory(history.slice(0, 10));
  }
})

const formatAmount = (amount: number) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatProfit = (bet: any) => {
  if (bet.status === 'won') {
    // Рассчитываем выигрыш: ставка × коэффициент, округляем до целого
    const winAmount = Math.round(bet.bet_amount * bet.crash_coefficient);
    return formatAmount(winAmount);
  } else if (bet.status === 'lost') {
    return '—'; // Прочерк для проигрышных ставок
  } else {
    return formatAmount(0); // Для pending
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
      params: { limit: 10 } // Запрашиваем только 10 последних ставок
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
/* Стили остаются без изменений */
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
  font-size: 16px;
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
  width: 16px;
  height: 16px;
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
  
  .bet-single-row {
    gap: 8px;
  }
  
  .bet-number {
    font-size: 12px;
  }
  
  .bet-time {
    font-size: 10px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 12px;
  }
  
  .bet-multiplier-panel {
    font-size: 12px;
    padding: 4px 6px;
    min-width: 45px;
  }
  
  .currency-icon {
    width: 12px;
    height: 12px;
  }
  
  .bet-amount-section,
  .bet-profit-section {
    min-width: 60px;
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
  
  .bet-single-row {
    gap: 6px;
  }
  
  .bet-number-time {
    min-width: 50px;
  }
  
  .bet-number {
    font-size: 11px;
  }
  
  .bet-time {
    font-size: 9px;
  }
  
  .bet-amount,
  .bet-profit {
    font-size: 11px;
  }
  
  .bet-multiplier-panel {
    font-size: 11px;
    padding: 3px 5px;
    min-width: 40px;
  }
  
  .currency-icon {
    width: 11px;
    height: 11px;
  }
  
  .bet-amount-section,
  .bet-profit-section {
    min-width: 55px;
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