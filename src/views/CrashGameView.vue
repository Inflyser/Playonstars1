<template>

    <div class="home">
      <TelegramHeader />
      <TelegramHeader2 title="Crash Game" />

        <!-- График игры -->
        <div class="game-graph">
          <div class="multiplier-display" :class="{ growing: isGameActive }">
            {{ currentMultiplier.toFixed(2) }}x
          </div>
          <div class="graph-canvas" ref="graphCanvas"></div>
        </div>

        <BettingPanel />

        <BettingPanel />


        <!-- Статус игры -->
        <div class="game-status">
          <div class="phase-badge" :class="gameState.phase">
            {{ phaseText }}
          </div>
          <div class="timer" v-if="gameState.phase === 'betting'">
            {{ gameState.timeRemaining }}s
          </div>
        </div>

        <!-- История игр -->
        <div class="game-history">
          <h4>История</h4>
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

        <!-- Панель ставок -->
        <div class="betting-panel" v-if="gameState.phase === 'betting'">
          <div class="balance-info">
            <span>Баланс: {{ userStore.balance.stars_balance.toFixed(2) }} stars</span>
          </div>

          <div class="bet-amount">
            <input
              v-model="betAmount"
              type="number"
              placeholder="Сумма ставки"
              :min="1"
              :max="userStore.balance.stars_balance"
              class="bet-input"
            />
            <button 
              @click="setBetAmount(userStore.balance.stars_balance)"
              class="max-btn"
            >
              MAX
            </button>
          </div>

          <div class="auto-cashout">
            <label>Авто-вывод (x):</label>
            <input
              v-model="autoCashout"
              type="number"
              placeholder="2.00"
              step="0.1"
              min="1.1"
              class="cashout-input"
            />
          </div>

          <button
            @click="placeBet"
            :disabled="!canPlaceBet || isBetting"
            class="place-bet-btn"
            :class="{ disabled: !canPlaceBet }"
          >
            {{ isBetting ? 'Размещение...' : `Поставить ${betAmount || 0} stars` }}
          </button>
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
    
      <div class="divider"></div>

      <div class="balance-view">
            <!-- Панель с кнопками -->
        <ButtonTop v-model="selectedPaymentMethod" />

        <!-- Контент в зависимости от выбранного метода -->
        <div class="payment-content">
          <TopAll v-if="selectedPaymentMethod === 'top'" />
          <Top10 v-if="selectedPaymentMethod === 'top10'" />
          <TopMy v-if="selectedPaymentMethod === 'mytop'" />
        </div>
      </div>

      <!-- Плавающая панель навигации -->
      <BottomNavigation />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useGameStore } from '@/stores/useGameStore'
import { useUserStore } from '@/stores/useUserStore'
import { useWebSocket } from '@/composables/useWebSocket'
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'

const gameStore = useGameStore()
const userStore = useUserStore()
const { connectToCrashGame, placeCrashBet, cashOut } = useWebSocket()

const betAmount = ref('')
const autoCashout = ref('')
const graphCanvas = ref<HTMLDivElement | null>(null)

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

const phaseText = computed(() => {
  const phases = {
    waiting: 'Ожидание',
    betting: 'Ставки',
    flying: 'Полет!',
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
  betAmount.value = amount.toString()
}

const placeBet = async () => {
  if (!betAmount.value || parseFloat(betAmount.value) <= 0) return
  
  const amount = parseFloat(betAmount.value)
  const cashoutValue = autoCashout.value ? parseFloat(autoCashout.value) : undefined

  try {
    await gameStore.placeBet(amount, cashoutValue)
    placeCrashBet(amount, cashoutValue)
  } catch (err) {
    console.error('Failed to place bet:', err)
  }
}

const doCashOut = async () => {
  try {
    await gameStore.cashOut()
    cashOut()
  } catch (err) {
    console.error('Failed to cash out:', err)
  }
}

const prepareNewGame = () => {
  gameStore.resetBet()
  betAmount.value = ''
  autoCashout.value = ''
}

// Lifecycle
onMounted(async () => {
  try {
    await connectToCrashGame()
  } catch (err) {
    console.error('Failed to connect to crash game:', err)
  }
})

// Watch for game phase changes
watch(() => gameState.value.phase, (newPhase) => {
  if (newPhase === 'finished') {
    setTimeout(prepareNewGame, 5000)
  }
})


import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'

import ButtonTop from '@/components/layout/ButtonTop.vue'
import Top10 from '@/components/ui/topCrash/Top10.vue'
import TopAll from '@/components/ui/topCrash/TopAll.vue'
import TopMy from '@/components/ui/topCrash/TopMy.vue'

import BettingPanel from '@/components/layout/BettingPanel.vue'


const selectedPaymentMethod = ref('top')
</script>

<style scoped>
.crash-game {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1f3b 0%, #13162b 100%);
  color: white;
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
  position: relative;
  height: 200px;
}

.multiplier-display {
  font-size: 2.5em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.multiplier-display.growing {
  animation: pulse 0.5s infinite alternate;
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.05); }
}

.graph-canvas {
  width: 100%;
  height: 100px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.game-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.phase-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  background: #6366f1;
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.history-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.history-item {
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  font-weight: bold;
  min-width: 60px;
  text-align: center;
}

.history-item.crashed {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
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


</style>
