<template>
    <div class="home">
        <TelegramHeader />




        <!-- История игр -->
        <div class="game-history">
            <div class="history-list">
                <div 
                    v-for="game in gameState.history.slice(0, 5)" 
                    :key="game.gameId" 
                    class="history-item"
                    :class="{ crashed: game.multiplier < 2 }"
                >
                    {{ game.multiplier.toFixed(2) }}x
                </div>
            </div>
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
            <div class="result-header">
              <h3>Игра завершена!</h3>
              <div class="final-multiplier">
                Множитель: x{{ gameState.multiplier.toFixed(2) }}
              </div>
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
           
            <div class="phase-badge" :class="gameState.phase">
                {{ phaseText }}
            </div>
            <div class="timer" v-if="gameState.phase === 'betting'">
                {{ gameState.timeRemaining }}s
            </div>
        </div>



        <BettingPanel 
          v-model:betAmount="betAmountNumber"
          :maxAmount="userStore.balance.stars_balance"
          :gamePhase="gameState.phase"
          :currentMultiplier="currentMultiplier"
          @place-bet="handlePlaceBet"
          @cash-out="doCashOut"
        />

        <!-- Панель ставок -->
        <div class="betting-panel" v-if="gameState.phase === 'betting'">
            <div class="balance-info">
                <span>Баланс: {{ userStore.balance.stars_balance.toFixed(2) }} stars</span>
            </div>

        </div>

        <!-- Панель игры -->
        <div class="game-panel" v-else-if="gameState.phase === 'flying'">
            <div class="current-bet" v-if="currentUserBet">
                <div class="bet-info">
                    <span>Ставка: {{ currentUserBet.amount }} stars</span>
                    <span>Текущий выигрыш: {{ currentProfit.toFixed(2) }} stars</span>
                </div>
                
                <button
                    @click="doCashOut"
                    :disabled="!canCashOut"
                    class="cashout-btn"
                    :class="{ disabled: !canCashOut }"
                >
                    Вывести {{ currentMultiplier.toFixed(2) }}x
                </button>
            </div>

            <div class="players-list">
                <div class="players-title">Игроки ({{ gameState.players.length }})</div>
                <div 
                    v-for="player in visiblePlayers" 
                    :key="player.userId" 
                    class="player-item"
                >
                    <img :src="player.avatar" class="player-avatar" />
                    <span class="player-name">{{ player.username }}</span>
                    <span class="player-bet">{{ player.betAmount }} stars</span>
                    <span 
                        v-if="player.cashoutMultiplier" 
                        class="player-cashout"
                    >
                        Вывел {{ player.cashoutMultiplier }}x
                    </span>
                </div>
            </div>
        </div>

        <!-- Результат игры -->
        <div class="result-panel" v-else-if="gameState.phase === 'finished'">
            <div class="result-message">
                <h3>Игра завершена!</h3>
                <p>Множитель: {{ gameState.multiplier.toFixed(2) }}x</p>
                
                <div v-if="currentUserBet" class="your-result">
                    <p>Ваша ставка: {{ currentUserBet.amount }} stars</p>
                    <p :class="{ profit: (currentUserBet.profit || 0) > 0, loss: (currentUserBet.profit || 0) === 0 }">
                        Результат: {{ (currentUserBet.profit || 0) > 0 ? '+' + (currentUserBet.profit || 0).toFixed(2) : '0' }} stars
                    </p>
                </div>

                <button @click="prepareNewGame" class="play-again-btn">
                    Играть снова
                </button>
            </div>
        </div>

        <!-- Ожидание игры -->
        <div class="waiting-panel" v-else>
            <div class="waiting-message">
                <h3>Ожидание следующей игры...</h3>
                <p>Новая игра начнется через {{ gameState.timeRemaining }} секунд</p>
            </div>
        </div>

        <!-- Уведомления -->
        <div v-if="gameError" class="error-notification">
            {{ gameError }}
        </div>

        <div class="debug-info" v-if="false"> <!-- поставьте true для дебага -->
            <p>Локальный баланс: {{ userStore.balance.stars_balance }}</p>
            <p>Ставка: {{ currentUserBet?.amount }}</p>
            <p>Выигрыш: {{ currentUserBet?.profit }}</p>
            <button @click="userStore.fetchBalance()">Обновить баланс</button>
            <button @click="userStore.syncBalance()">Синхронизировать</button>
        </div>

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
    await gameStore.loadGameHistory()
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
}

.history-list {
  display: flex;
  gap: 4px; /* Еще меньше отступ между элементами */
  overflow-x: auto;
  padding: 2px 0; /* Минимальный падинг */
}

.history-item {
  margin: 0px 0px 8px 0px; /* Уменьшил нижний margin */
  border: 1px solid #4B7ED0; /* Тоньше бордер */
  border-radius: 6px; /* Меньше скругление */
  background: #355391;
  font-weight: bold;
  text-align: center;
  font-size: 10px; /* Еще меньше шрифт */
  width: 15%; /* Уже */
  min-width: 40px; /* Уменьшил минимальную ширину */
  padding: 2px 1px; /* Минимальный падинг */
  box-sizing: border-box;
  flex-shrink: 0;
  line-height: 1.2; /* Уменьшил межстрочный интервал */
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
