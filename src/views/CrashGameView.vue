<template>
    <div class="home">
        <TelegramHeader />




        <!-- История игр -->
        <div 
          v-for="(game, index) in gameState.history" 
          :key="index"
          class="history-item"
          :class="{
            'multiplier-low': game.multiplier < 2,
            'multiplier-medium': game.multiplier >= 2 && game.multiplier < 3,
            'multiplier-high': game.multiplier >= 7
          }"
        >
          {{ game.multiplier.toFixed(2) }}x
        </div>

        <!-- График игры -->
        <div class="game-graph">
          <template v-if="gameState.phase !== 'finished'">
            <img src="@/assets/images/crashfon.svg" class="graph-background">
            <img src="@/assets/images/kpanel.svg" class="panels-crash">
            <div class="multiplier-display" :class="{ growing: isGameActive }">
              x{{ currentMultiplier.toFixed(2) }}
            </div>
            <canvas ref="graphCanvas" class="graph-canvas"></canvas>
            <img 
              v-if="rocketPosition" 
              :src="rocketImageSrc" 
              class="rocket-overlay"
              :style="{
                left: rocketPosition.x + 'px',
                top: rocketPosition.y + 'px'
              }"
            >
          </template>

          <!-- Результаты игры -->
          <div v-else class="game-results">
            <img src="@/assets/images/crashfon.svg" class="graph-background">
            <img src="@/assets/images/kpanel.svg" class="panels-crash">
            <div class="multiplier-display" :class="{ growing: isGameActive }">
              x{{ currentMultiplier.toFixed(2) }}
            </div>
            <div class="result-header">
              <h3>Игра завершена!</h3>
            </div>

            <div class="player-result" v-if="currentUserBet">
              <div class="result-icon" :class="{ success: (currentUserBet.profit || 0) > 0, failure: (currentUserBet.profit || 0) <= 0 }">
                {{ (currentUserBet.profit || 0) > 0 ? '🎉' : '💥' }}
              </div>
              <div class="result-details">
                <p>Ваша ставка: <strong>{{ currentUserBet.amount }} stars</strong></p>
                <p :class="{ profit: (currentUserBet.profit || 0) > 0, loss: (currentUserBet.profit || 0) <= 0 }">
                  Результат: <strong>{{ (currentUserBet.profit || 0) > 0 ? '+' + (currentUserBet.profit || 0).toFixed(2) : '0' }} stars</strong>
                </p>
                <p v-if="currentUserBet.cashoutMultiplier" class="cashout-info">
                  Вывели на: x{{ currentUserBet.cashoutMultiplier.toFixed(2) }}
                </p>
                <p v-else class="cashout-info">
                  Не успели вывести
                </p>
              </div>
            </div>

            <div class="no-bet" v-else>
              <div class="result-icon">👀</div>
              <p style="margin: -10px;">Вы не делали ставку в этой игре</p>
            </div>
          </div>
        </div>

        <!-- Статус игры -->
        <div class="game-status">
            <div class="timer" v-if="gameState.phase === 'betting'">
              {{ bettingTimer }}s
            </div>
        </div>


     
        <BettingPanel 
          v-model:betAmount="firstBetAmount"
          :maxAmount="userStore.balance.stars_balance"
          :gamePhase="gameState.phase"
          :currentMultiplier="currentMultiplier"
          @place-bet="handleFirstBet"
          @cash-out="doFirstCashOut"
        />

        <!-- Вторая панель ставок -->
        <BettingPanel 
          v-model:betAmount="secondBetAmount"
          :maxAmount="userStore.balance.stars_balance"
          :gamePhase="gameState.phase"
          :currentMultiplier="currentMultiplier"
          @place-bet="handleSecondBet"
          @cash-out="doSecondCashOut"
        />
     


        <div class="divider"></div>

        <!-- Топ игроков -->
        <div class="balance-view">
            <ButtonTop v-model="selectedPaymentMethod" />
            
            <div class="payment-content">
                <TopAll v-if="selectedPaymentMethod === 'top'" />
                <Top10 v-if="selectedPaymentMethod === 'top10'" />
                <TopMy v-if="selectedPaymentMethod === 'mytop'" />
            </div>
        </div>

        <BottomNavigation />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useGameStore } from '@/stores/useGameStore'
import { useUserStore } from '@/stores/useUserStore'
import { useWebSocket } from '@/composables/useWebSocket'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import ButtonTop from '@/components/layout/ButtonTop.vue'
import Top10 from '@/components/ui/topCrash/Top10.vue'
import TopAll from '@/components/ui/topCrash/TopAll.vue'
import TopMy from '@/components/ui/topCrash/TopMy.vue'
import BettingPanel from '@/components/layout/BettingPanel.vue' 

const gameStore = useGameStore()
const userStore = useUserStore()
const { connectToCrashGame, placeCrashBet, cashOut } = useWebSocket()

const betAmountNumber = ref(100) // ✅ Теперь number
const autoCashout = ref('')
const selectedPaymentMethod = ref('top')
const firstBetAmount = ref(100)
const secondBetAmount = ref(50) // Можно задать разное начальное значение

interface CrashGameHistory {
  id: number
  game_id: number
  multiplier: number
  crashed_at: number
  total_players: number
  total_bet: number
  total_payout: number
  timestamp: string
}

interface CrashGameState {
  // ... другие поля ...
  history: CrashGameHistory[]
}

const crashGame = ref<CrashGameState>({
  // ... другие поля ...
  history: []
})

// Computed properties
const gameState = computed(() => gameStore.crashGame)
const currentMultiplier = computed(() => gameState.value.multiplier)
const isGameActive = computed(() => gameStore.isGameActive)
const canPlaceBet = computed(() => gameStore.canPlaceBet)
const canCashOut = computed(() => gameStore.canCashOut)
const isBetting = computed(() => gameStore.isBetting)
const currentUserBet = computed(() => gameStore.userBet)
const currentProfit = computed(() => gameStore.currentProfit)
const gameError = computed(() => gameStore.error)


const handleFirstBet = (betData: any) => {
  console.log('Ставка с первой панели:', betData)
  // Ваша логика обработки ставки
  const amount = betData.amount
  const cashoutValue = betData.coefficient ? parseFloat(betData.coefficient) : undefined
  
  if (!amount || amount <= 0) return
  
  try {
    gameStore.placeBet(amount, cashoutValue)
    placeCrashBet(amount, cashoutValue)
  } catch (err) {
    console.error('Failed to place bet from first panel:', err)
  }
}

const handleSecondBet = (betData: any) => {
  console.log('Ставка со второй панели:', betData)
  // Можно добавить разную логику для второй панели
  const amount = betData.amount
  const cashoutValue = betData.coefficient ? parseFloat(betData.coefficient) : undefined
  
  if (!amount || amount <= 0) return
  
  try {
    gameStore.placeBet(amount, cashoutValue)
    placeCrashBet(amount, cashoutValue)
  } catch (err) {
    console.error('Failed to place bet from second panel:', err)
  }
}

const doFirstCashOut = async () => {
  try {
    await gameStore.cashOut();
    cashOut();
    // Дополнительная логика для первой панели
  } catch (error) {
    console.error('Failed to cash out from first panel:', error);
  }
};

const doSecondCashOut = async () => {
  try {
    await gameStore.cashOut();
    cashOut();
    // Дополнительная логика для второй панели
  } catch (error) {
    console.error('Failed to cash out from second panel:', error);
  }
};


const totalBet = computed(() => {
    return gameState.value.players.reduce((sum: number, player: any) => sum + player.betAmount, 0)
})

const phaseText = computed(() => {
    const phases = {
        waiting: 'Ожидание',
        betting: 'Ставки',
        flying: 'Игра идет!',
        crashed: 'Крах!',
        finished: 'Завершено'
    }
    return phases[gameState.value.phase] || 'Ожидание'
})

const visiblePlayers = computed(() => {
    return gameState.value.players.slice(0, 10)
})

// Methods
const setBetAmount = (amount: number) => {
    betAmountNumber.value = amount // ✅ Просто присваиваем number
}

const placeBet = async (betData?: any) => {
    // ✅ Теперь betAmountNumber уже number, не нужно парсить
    const amount = betData?.amount || betAmountNumber.value
    const cashoutValue = betData?.coefficient || (autoCashout.value ? parseFloat(autoCashout.value) : undefined)

    if (!amount || amount <= 0) return
    
    try {
        await gameStore.placeBet(amount, cashoutValue)
        placeCrashBet(amount, cashoutValue)
    } catch (err) {
        console.error('Failed to place bet:', err)
    }
}

// Новый метод для обработки ставки
const handlePlaceBet = (betData: any) => {
    const amount = betData.amount
    const cashoutValue = betData.coefficient ? parseFloat(betData.coefficient) : undefined

    if (!amount || amount <= 0) return
    
    try {
        gameStore.placeBet(amount, cashoutValue)
        placeCrashBet(amount, cashoutValue)
    } catch (err) {
        console.error('Failed to place bet:', err)
    }
}

const doCashOut = async () => {
    try {
        await gameStore.cashOut();
        cashOut();
        
        
        // ✅ ДВОЙНАЯ ПРОВЕРКА СИНХРОНИЗАЦИИ
        setTimeout(async () => {
            const syncedBalance = await userStore.syncBalance();
            if (syncedBalance) {
                console.log('Balance synced successfully:', syncedBalance);
            }
        }, 1000);
        
    } catch (error) {
        console.error('Failed to cash out:', error);
    }
};

// Добавляем watch для отслеживания изменений баланса
watch(() => userStore.balance, (newBalance) => {
    console.log('Balance changed:', newBalance);
}, { deep: true });


const prepareNewGame = () => {
  gameStore.resetBet()
  betAmountNumber.value = 10
  autoCashout.value = ''
  // Останавливаем анимацию графика если она идет
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
    animationFrame.value = null
  }
}

// ГРАФИК

import rocketImageSrc from '@/assets/images/space-monkey-character.svg'

// Переменные
const graphCanvas = ref<HTMLCanvasElement | null>(null)
const graphContext = ref<CanvasRenderingContext2D | null>(null)
const rocketPosition = ref<{x: number; y: number} | null>(null)
const animationFrame = ref<number | null>(null)

// Инициализация графика
const initGraph = () => {
  if (!graphCanvas.value) return
  
  graphCanvas.value.width = graphCanvas.value.offsetWidth
  graphCanvas.value.height = graphCanvas.value.offsetHeight
  
  graphContext.value = graphCanvas.value.getContext('2d')
  drawGraph()
}

// Функция отрисовки графика
const drawGraph = () => {
  if (!graphContext.value || !graphCanvas.value) return
  
  const ctx = graphContext.value
  const width = graphCanvas.value.width
  const height = graphCanvas.value.height
  
  // Очистка canvas
  ctx.clearRect(0, 0, width, height)
  
  // Параметры графика
  const freezeMultiplier = 2.5
  const freezePointX = width * 0.67
  
  // Вычисляем прогресс
  let progress = currentMultiplier.value / freezeMultiplier
  let renderProgress = Math.min(progress, 1)
  
  // Координаты
  const baseStartY = height * 0.9
  const startY = baseStartY - (baseStartY * 0.3 * renderProgress)
  const endX = freezePointX * renderProgress
  const endY = startY - (startY * renderProgress * renderProgress * 0.7)
  
  // Градиент для области
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0.0, '#534081B2')
  gradient.addColorStop(1.0, '#2C214330')
  
  // Рисуем область под графиком
  ctx.beginPath()
  ctx.fillStyle = gradient
  ctx.moveTo(0, baseStartY)
  
  const points = 20
  for (let i = 1; i <= points; i++) {
    const t = i / points
    const x = endX * t
    const y = startY - (startY * t * t * renderProgress * 0.7)
    ctx.lineTo(x, y)
  }
  
  ctx.lineTo(endX, baseStartY)
  ctx.lineTo(0, baseStartY)
  ctx.closePath()
  ctx.fill()
  
  // Рисуем линию графика
  ctx.beginPath()
  ctx.lineWidth = 2
  ctx.strokeStyle = '#534081'
  ctx.moveTo(0, startY)
  
  for (let i = 1; i <= points; i++) {
    const t = i / points
    const x = endX * t
    const y = startY - (startY * t * t * renderProgress * 0.7)
    ctx.lineTo(x, y)
  }
  
  ctx.stroke()
  
  // Обновляем позицию ракеты
  updateRocketPosition(endX, endY)
  
  // Продолжаем анимацию если игра активна
  if (isGameActive.value) {
    animationFrame.value = requestAnimationFrame(drawGraph)
  }
}

// Функция обновления позиции ракеты
const updateRocketPosition = (endX: number, endY: number) => {
  if (!graphCanvas.value) return
  
  const canvasRect = graphCanvas.value.getBoundingClientRect()
  const scrollX = window.scrollX || window.pageXOffset
  const scrollY = window.scrollY-160 || window.pageYOffset
  
  rocketPosition.value = {
    x: canvasRect.left + endX + scrollX,
    y: canvasRect.top + endY + scrollY + 10
  }
}

// Загрузка при монтировании
onMounted(async () => {
  try {
    await connectToCrashGame()
    await gameStore.loadGameHistory(15)
    initGraph()
  } catch (err) {
    console.error('Failed to initialize crash game:', err)
  }
})


// Следим за изменением множителя
watch(currentMultiplier, () => {
  if (isGameActive.value && !animationFrame.value) {
    animationFrame.value = requestAnimationFrame(drawGraph)
  }
})

const bettingTimer = ref(0)
// Следим за фазой игры
watch(() => gameState.value.phase, (newPhase) => {
  if (newPhase === 'finished') {
    setTimeout(prepareNewGame, 5000)
  } else if (newPhase === 'waiting' || newPhase === 'betting') {
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
      animationFrame.value = null
    }
    rocketPosition.value = null
    drawGraph()
  }
  if (newPhase === 'betting') {
    bettingTimer.value = gameState.value.timeRemaining || 5

    const timerInterval = setInterval(() => {
      if (bettingTimer.value > 0) {
        bettingTimer.value--
      } else {
        clearInterval(timerInterval)
      }
    }, 1000)
  }
})


// Lifecycle

onMounted(async () => {
  try {
    await connectToCrashGame()
    await gameStore.loadGameHistory()
    
    // Инициализация графика
    initGraph()
  } catch (err) {
    console.error('Failed to initialize crash game:', err)
  }
})

// Перерисовываем график при изменении множителя
watch(currentMultiplier, () => {
  drawGraph()
})


</script>

<style scoped>

.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}


.game-container {
  padding: 16px;
  max-width: 400px;
  margin: 0 auto;
}

.game-graph {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  width: 95%;
  position: relative;
  height: 35vh;
  border: 1px solid #4479D98A;
  margin: 20px 0px 20px 2.5%;
  z-index: 2;

}

.rocket-overlay {
  position: absolute;
  width: 124px;
  height: 124px;
  z-index: 1000; /* Очень высокий z-index поверх всего */
  pointer-events: none; /* Чтобы не мешала кликам */
  transform: translate(-50%, -50%); /* Центрирование */
}

.graph-background {
  border-radius: 16px;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -2; /* Фон должен быть позади всего контента */
}
.panels-crash {
  position: absolute;
  top: -1.5%;
  left: 10%;
  width: 80%;
  height: 25%;
  z-index: -1; /* Фон должен быть позади всего контента */
}

.multiplier-display {
  position: absolute;
  left: 39%;
  top: 1%;
  font-size: 1.9em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  color: #ffffff;
}

.multiplier-display.growing {
  animation: pulse 0.5s infinite alternate;
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.05); }
}

.graph-canvas {
  position: absolute;
  left: 0%;
  top: 32%;
  width: 100%;
  height: 25vh;
  border-radius: 15px;
}

.game-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px;
}

.phase-badge {
  border-radius: 20px;
  font-weight: bold;
  background: #6366f1;
  width: 25%;
}

.phase-badge.betting { background: #f59e0b; }
.phase-badge.flying { background: #10b981; }
.phase-badge.crashed { background: #ef4444; }
.phase-badge.finished { background: #6b7280; }

.timer {
  font-size: 1.2em;
  font-weight: bold;
  color: #f59e0b;
}

.game-history {
  width: 95%;
  margin: 8px 0px 15px 2.5%;
  border-bottom: 1px solid #25213C;
  overflow-x: auto;
  white-space: nowrap;
  padding-bottom: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* Скрываем скроллбар */
.game-history::-webkit-scrollbar {
  display: none;
}

.history-list {
  display: inline-flex;
  gap: 6px;
  padding: 5px 0;
}

.history-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 45px;
  height: 45px;
  border: 2px solid #4B7ED0; /* Синий по умолчанию */
  border-radius: 8px;
  background: #355391; /* Синий по умолчанию */
  font-weight: bold;
  text-align: center;
  font-size: 11px;
  flex-shrink: 0;
  padding: 0;
  color: white;
  transition: all 0.3s ease;
}

/* Коэффициент меньше 2 - синий */
.history-item.multiplier-low {
  border-color: #4B7ED0;
  background: #355391;
}

/* Коэффициент от 2 до 2.99 - фиолетовый */
.history-item.multiplier-medium {
  border-color: #764BD0;
  background: #5A3A9E;
}

/* Коэффициент больше 7 - зеленый */
.history-item.multiplier-high {
  border-color: #83CE38;
  background: #67A32B;
}

/* Индикатор прокрутки */
.game-history:after {
  content: '';
  position: absolute;
  right: 2.5%;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: linear-gradient(90deg, transparent, #1B152F);
  pointer-events: none;
}

.betting-panel,
.game-panel,
.result-panel,
.waiting-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.balance-info {
  margin-bottom: 12px;
  font-weight: bold;
}

.bet-amount {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.bet-input,
.cashout-input {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: #000;
}

.max-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #6366f1;
  color: white;
  cursor: pointer;
}

.place-bet-btn,
.cashout-btn,
.play-again-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  margin-top: 12px;
}

.place-bet-btn {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #000;
}

.place-bet-btn.disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.cashout-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.cashout-btn.disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.play-again-btn {
  background: #6366f1;
  color: white;
}

.current-bet {
  margin-bottom: 16px;
}

.bet-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.players-list {
  max-height: 200px;
  overflow-y: auto;
}

.players-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #00ff88;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 4px;
}

.player-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.player-name {
  flex: 1;
  font-size: 0.9em;
}

.player-bet {
  color: #00ff88;
  font-weight: bold;
}

.player-cashout {
  color: #f59e0b;
  font-size: 0.8em;
}

.result-message {
  text-align: center;
}

.your-result {
  margin: 16px 0;
}

.profit {
  color: #00ff88;
  font-weight: bold;
}

.loss {
  color: #ef4444;
  font-weight: bold;
}

.error-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #ef4444;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  z-index: 1000;
}

.waiting-message {
  text-align: center;
  color: #9ca3af;
}



.game-stats {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(255, 255, 255, 0.1);
    padding: 12px;
    border-radius: 8px;
    min-width: 80px;
}

.history-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 12px;
}

.multiplier {
    font-weight: bold;
    font-size: 1.1em;
}

.players {
    font-size: 0.8em;
    opacity: 0.8;
}




.game-results {
  padding: 20px;
  text-align: center;
  color: white;
}

.result-header {
  margin-bottom: 20px;
}

.result-header h3 {
  margin: 0 0 10px 0;
  color: #fff;
}

.final-multiplier {
  font-size: 1.5em;
  font-weight: bold;
  color: #ffffff;
}

.player-result {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.result-icon {
  font-size: 3em;
}

.result-icon.success {
  animation: bounce 0.5s infinite alternate;
}

.result-icon.failure {
  opacity: 0.8;
}

@keyframes bounce {
  from { transform: scale(1); }
  to { transform: scale(1.1); }
}

.result-details {
  text-align: left;
}

.result-details p {
  margin: 5px 0;
}

.profit {
  color: #00ff88;
  font-weight: bold;
}

.loss {
  color: #ff6b6b;
  font-weight: bold;
}

.cashout-info {
  color: #a0a0b0;
  font-size: 0.9em;
}

.no-bet {
  padding: 10px;
}

.no-bet .result-icon {
  font-size: 2.5em;
  margin: 10px;
}

</style>
