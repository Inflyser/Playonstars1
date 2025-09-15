<template>
    <div class="home">
        <TelegramHeader />



        <div class="game-history">
          <div class="history-list">
            <div
              v-for="(game, index) in gameState.history" 
              :key="index"
              class="history-item"
              :class="{
                'multiplier-low': game.multiplier < 2.9,
                'multiplier-medium': game.multiplier >= 2.9 && game.multiplier < 7,
                'multiplier-high': game.multiplier >= 7
              }"
            >
              {{ game.multiplier.toFixed(2) }}x
            </div>
          </div>
        
          <!-- Фиксированная панелька справа - теперь кнопка -->
          <button class="history-scroll-indicator" @click="handleOpenModal">
            <div class="indicator-icon">
              <img src="@/assets/images/clock.svg" alt="scroll">
            </div>
            <div class="indicator-shadow"></div>
          </button >
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
  <!-- Результаты игры -->
          <div v-else class="game-results">
            <img src="@/assets/images/crashfon.svg" class="graph-background">
            <img src="@/assets/images/kpanel.svg" class="panels-crash">

            <div class="result-content">
              <!-- Заголовок с анимацией -->
              <div class="result-header">
                <div class="result-title" :class="{ 'crashed': currentMultiplier < 1 }">
                  <template v-if="currentMultiplier < 1">
                    <span class="crash-icon">💥</span>
                    <h3>Крах!</h3>
                  </template>
                  <template v-else>
                    <span class="success-icon">🎯</span>
                    <h3>Игра завершена!</h3>
                  </template>
                </div>
                <div class="final-multiplier" :class="{ 
                  'low': currentMultiplier < 2, 
                  'medium': currentMultiplier >= 2 && currentMultiplier < 5,
                  'high': currentMultiplier >= 5
                }">
                  x{{ currentMultiplier.toFixed(2) }}
                </div>
              </div>
            
              <!-- Результат пользователя -->
              <div class="user-result-container">
                <div class="player-result" v-if="currentUserBet">
                  <div class="result-badge" :class="{ 
                    'success': (currentUserBet.profit || 0) > 0, 
                    'failure': (currentUserBet.profit || 0) <= 0 
                  }">
                    <div class="badge-icon">
                      {{ (currentUserBet.profit || 0) > 0 ? '🎉' : '💥' }}
                    </div>
                    <div class="badge-text">
                      {{ (currentUserBet.profit || 0) > 0 ? 'ПОБЕДА' : 'ПРОИГРЫШ' }}
                    </div>
                  </div>
                
                  <div class="result-details">
                    <div class="detail-row">
                      <span class="label">Ставка:</span>
                      <span class="value bet-amount">{{ currentUserBet.amount }} stars</span>
                    </div>

                    <div class="detail-row" :class="{ 
                      'profit': (currentUserBet.profit || 0) > 0, 
                      'loss': (currentUserBet.profit || 0) <= 0 
                    }">
                      <span class="label">Результат:</span>
                      <span class="value result-amount">
                        {{ (currentUserBet.profit || 0) > 0 ? '+' + (currentUserBet.profit || 0).toFixed(2) : '0' }} stars
                      </span>
                    </div>
                  
                    <div class="detail-row cashout-info">
                      <span class="label">Вывели на:</span>
                      <span class="value cashout-multiplier" v-if="currentUserBet.cashoutMultiplier">
                        x{{ currentUserBet.cashoutMultiplier.toFixed(2) }}
                      </span>
                      <span class="value not-cashed" v-else>
                        Не успели вывести
                      </span>
                    </div>
                  </div>
                </div>
              
                <div class="no-bet" v-else>
                  <div class="no-bet-icon">👀</div>
                  <div class="no-bet-text">
                    <p>Вы не делали ставку</p>
                    <p class="subtext">в этой игре</p>
                  </div>
                </div>
              </div>
            
              <!-- Автоматическое обновление через WebSocket -->
              <div class="auto-update-info">
                <div class="update-icon">🔄</div>
                <p class="update-text">Новая игра начнется автоматически</p>
              </div>
            </div>
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
     


                <!-- Модальное окно истории коэффициентов -->
        <div v-if="showHistoryModal" class="history-modal-overlay" @click.self="showHistoryModal = false">
          <div class="history-modal">
            <div class="modal-header">
              <h2>{{ t('histor') }}</h2>
              <button class="close-button" @click="showHistoryModal = false">
                <img src="@/assets/images/close.svg" alt="close">
              </button>
            </div>
          
            <div class="modal-content">
              <div class="full-history-list">
                <div
                  v-for="(game, index) in gameState.history"
                  :key="index"
                  class="full-history-item"
                  :class="{
                    'multiplier-low': game.multiplier < 2.9,
                    'multiplier-medium': game.multiplier >= 2.9 && game.multiplier < 7,
                    'multiplier-high': game.multiplier >= 7
                  }"
                >
                  <span class="multiplier-value">{{ game.multiplier.toFixed(2) }}x</span>
                </div>
              </div>
            </div>
          </div>
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
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

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

const showHistoryModal = ref(false)

const handleOpenModal = () => {
    console.log('Кнопка нажата!');
    showHistoryModal.value = true;
}

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


onMounted(async () => {
  try {
    await connectToCrashGame()
    await gameStore.loadGameHistory(100)
    
    // Инициализация графика
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
    position: relative; /* Важно для абсолютного позиционирования дочерних элементов */
    width: 95%;
    margin: 8px 0px 15px 2.5%;
    border-bottom: 1px solid #25213C;
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 10px;
}

.game-history::-webkit-scrollbar {
  display: none;
}

.history-list {
    display: inline-flex;
    gap: 4px;
    padding: 5px 45px 5px 5px; /* Оставляем место для кнопки справа */
    position: relative;
    z-index: 10;
}

.history-scroll-indicator {
    position: absolute;
    right: 3.5px;
    top: 35%;
    transform: translateY(-50%);
    width: 30px;
    height: 30px;
    z-index: 20;
    pointer-events: auto;
    background: none;
    border: none;
    cursor: pointer;
}

.indicator-icon {
  width: 35px;
  height: 35px;
  background: #241D49;
  border: 4px solid #100D1F;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 5000;
  cursor: pointer;
}

.indicator-icon img {
  width: 16px;
  height: 16px;
  object-fit: contain;
  filter: brightness(1.2);
}

.indicator-shadow {
  position: absolute;
  left: -15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 30px;
  background: linear-gradient(90deg, 
    #100D1F 0%, 
    #100D1F4A 100% /* 29% прозрачности в HEX = 4A */
  );
  filter: blur(10px);
  z-index: 1;
  border-radius: 4px 0 0 4px;
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
  min-width: 38px;        /* Уменьшили ширину */
  height: 28px;           /* Сильно уменьшили высоту */
  border: 1px solid #4B7ED0;
  border-radius: 6px;
  background: #355391;
  font-weight: bold;
  text-align: center;
  font-size: 9px;         /* Уменьшили шрифт */
  flex-shrink: 0;
  padding: 0;
  color: white;
  transition: all 0.2s ease;
  margin: 0 1px;          /* Уменьшили отступ между элементами */
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




/* Стили для модального окна */
/* Стили для модального окна */
.history-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 15px;
}

.history-modal {
  background: linear-gradient(135deg, #1B152F 0%, #180A24 100%);
  border-radius: 16px;
  border: 2px solid #4479D9;
  width: 100%;
  max-width: 95%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #2D2A40;
  background: rgba(36, 29, 73, 0.8);
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.1em;
  font-weight: 600;
}

.close-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.close-button img {
  width: 14px;
  height: 14px;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

/* ОБНОВЛЕННЫЕ СТИЛИ ДЛЯ 5 ЭЛЕМЕНТОВ В РЯД */
.full-history-list {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr)); /* Фиксировано 5 в ряд */
  gap: 6px; /* Минимальный отступ */
  padding: 5px;
}

.full-history-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 2px; /* Минимальный padding */
  border-radius: 6px;
  text-align: center;
  min-height: 25px; /* Компактная высота */
  aspect-ratio: 1/1; /* Квадратные элементы */
  transition: transform 0.2s ease;
}

.full-history-item:hover {
  transform: scale(1.05);
}

.full-history-item.multiplier-low {
  border: 1px solid #4B7ED0;
  background: linear-gradient(135deg, #355391 0%, #2A4175 100%);
}

.full-history-item.multiplier-medium {
  border: 1px solid #764BD0;
  background: linear-gradient(135deg, #5A3A9E 0%, #462C7A 100%);
}

.full-history-item.multiplier-high {
  border: 1px solid #83CE38;
  background: linear-gradient(135deg, #67A32B 0%, #4F7E21 100%);
}

.multiplier-value {
  font-size: 0.75em; /* Уменьшенный шрифт */
  font-weight: bold;
  margin-bottom: 2px;
  color: white;
  line-height: 1.1;
}

.game-time {
  font-size: 0.55em; /* Очень маленький шрифт */
  opacity: 0.8;
  color: #CCCCCC;
  line-height: 1;
}

/* Стили для скролла */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #4B7ED0;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #5A8DE0;
}

/* Адаптивность - сохраняем 5 в ряд на всех устройствах */
@media (max-width: 768px) {
  .full-history-list {
    grid-template-columns: repeat(5, minmax(0, 1fr)); /* Все равно 5 в ряд */
    gap: 4px; /* Еще меньше отступ */
  }
  
  .full-history-item {
    padding: 4px 1px;
    min-height: 40px;
    border-radius: 4px;
  }
  
  .multiplier-value {
    font-size: 0.7em;
  }
  
  .game-time {
    font-size: 0.5em;
  }
  
  .history-modal {
    max-width: 100%;
    max-height: 90vh;
  }
}

@media (max-width: 480px) {
  .full-history-list {
    grid-template-columns: repeat(5, minmax(0, 1fr)); /* Все равно 5 в ряд */
    gap: 3px;
  }
  
  .full-history-item {
    padding: 3px 1px;
    min-height: 35px;
    border-radius: 3px;
  }
  
  .multiplier-value {
    font-size: 0.65em;
  }
  
  .game-time {
    font-size: 0.45em;
  }
  
  .modal-header {
    padding: 10px 15px;
  }
  
  .modal-header h2 {
    font-size: 0.95em;
  }
}

/* Для очень маленьких экранов - уменьшаем еще больше */
@media (max-width: 320px) {
  .full-history-list {
    gap: 2px;
  }
  
  .full-history-item {
    min-height: 30px;
    padding: 2px 0;
  }
  
  .multiplier-value {
    font-size: 0.6em;
  }
  
  .game-time {
    font-size: 0.4em;
  }
}

.game-results {
  position: relative;
  padding: 20px;
  text-align: center;
  color: white;
  height: 35vh;
  border-radius: 16px;
  overflow: hidden;
}

.result-content {
  position: relative;
  z-index: 10;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.result-header {
  margin-bottom: 15px;
}

.result-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.result-title h3 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.crash-icon, .success-icon {
  font-size: 2em;
  animation: bounce 0.6s infinite alternate;
}

@keyframes bounce {
  from { transform: translateY(0px); }
  to { transform: translateY(-5px); }
}

.final-multiplier {
  font-size: 2.2em;
  font-weight: 900;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  margin: 8px 0;
  animation: pulse 1s infinite alternate;
}

@keyframes pulse {
  from { opacity: 0.8; transform: scale(1); }
  to { opacity: 1; transform: scale(1.05); }
}

.final-multiplier.low {
  color: #ff6b6b;
  text-shadow: 0 2px 10px rgba(255, 107, 107, 0.3);
}

.final-multiplier.medium {
  color: #f59e0b;
  text-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
}

.final-multiplier.high {
  color: #00ff88;
  text-shadow: 0 2px 10px rgba(0, 255, 136, 0.3);
}

.user-result-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
}

.player-result {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 300px;
}

.result-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 25px;
  margin-bottom: 20px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.result-badge.success {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 204, 106, 0.3) 100%);
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #00ff88;
}

.result-badge.failure {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(238, 90, 82, 0.3) 100%);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.badge-icon {
  font-size: 1.5em;
}

.badge-text {
  font-size: 0.9em;
}

.result-details {
  text-align: left;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  color: #a0a0b0;
  font-size: 0.9em;
  font-weight: 500;
}

.value {
  font-weight: 700;
  font-size: 1em;
}

.bet-amount {
  color: #ffffff;
}

.result-amount.profit {
  color: #00ff88;
}

.result-amount.loss {
  color: #ff6b6b;
}

.cashout-multiplier {
  color: #f59e0b;
}

.not-cashed {
  color: #a0a0b0;
  font-style: italic;
  font-size: 0.9em;
}

.no-bet {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  padding: 25px;
}

.no-bet-icon {
  font-size: 2.5em;
  opacity: 0.7;
}

.no-bet-text {
  text-align: center;
}

.no-bet-text p {
  margin: 0;
  font-size: 1.1em;
  font-weight: 600;
}

.no-bet-text .subtext {
  font-size: 0.9em;
  color: #a0a0b0;
  margin-top: 5px;
}

.auto-update-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  margin-top: 15px;
  animation: fadeInOut 2s infinite alternate;
}

@keyframes fadeInOut {
  from { opacity: 0.6; }
  to { opacity: 1; }
}

.update-icon {
  font-size: 1.2em;
}

.update-text {
  margin: 0;
  font-size: 0.9em;
  color: #a0a0b0;
  font-weight: 500;
}

/* Адаптивность */
@media (max-width: 768px) {
  .result-title h3 {
    font-size: 1.2em;
  }
  
  .final-multiplier {
    font-size: 1.8em;
  }
  
  .player-result {
    padding: 15px;
    max-width: 250px;
  }
  
  .result-badge {
    padding: 10px 15px;
  }
  
  .badge-text {
    font-size: 0.8em;
  }
  
  .auto-update-info {
    padding: 10px;
  }
  
  .update-text {
    font-size: 0.8em;
  }
}

@media (max-width: 480px) {
  .game-results {
    padding: 15px;
  }
  
  .result-title h3 {
    font-size: 1.1em;
  }
  
  .final-multiplier {
    font-size: 1.6em;
  }
  
  .player-result {
    padding: 12px;
    max-width: 220px;
  }
  
  .no-bet {
    padding: 20px;
  }
  
  .no-bet-icon {
    font-size: 2em;
  }
  
  .auto-update-info {
    flex-direction: column;
    gap: 5px;
    padding: 8px;
  }
  
  .update-text {
    font-size: 0.75em;
    text-align: center;
  }
}
</style>