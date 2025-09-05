<template>
    <div class="home">
        <TelegramHeader />
        <TelegramHeader2 title="Crash Game" />

        <!-- График игры -->
        <div class="game-graph">
            <div class="multiplier-display" :class="{ growing: isGameActive }">
                x{{ currentMultiplier.toFixed(2) }}
            </div>
            <div class="graph-canvas" ref="graphCanvas"></div>
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

        <BettingPanel 
              v-model:betAmount="betAmount"
              :maxAmount="userStore.balance.stars_balance"
              @place-bet="placeBet"
          />

        <!-- Панель ставок -->
        <div class="betting-panel" v-if="gameState.phase === 'betting'">
   



          
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

        <!-- Статистика игры -->
        <div class="game-stats" v-if="isGameActive">
            <div class="stat-item">
                <span>Игроков:</span>
                <span>{{ gameState.players.length }}</span>
            </div>
            <div class="stat-item">
                <span>Общая ставка:</span>
                <span>{{ totalBet }} stars</span>
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
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import ButtonTop from '@/components/layout/ButtonTop.vue'
import Top10 from '@/components/ui/topCrash/Top10.vue'
import TopAll from '@/components/ui/topCrash/TopAll.vue'
import TopMy from '@/components/ui/topCrash/TopMy.vue'

const gameStore = useGameStore()
const userStore = useUserStore()
const { connectToCrashGame, placeCrashBet, cashOut } = useWebSocket()

const betAmount = ref('')
const autoCashout = ref('')
const selectedPaymentMethod = ref('top')
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

const totalBet = computed(() => {
    return gameState.value.players.reduce((sum: number, player: any) => sum + player.betAmount, 0)
})

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
        // 1. Сохраняем ставку локально
        await gameStore.placeBet(amount, cashoutValue)
        
        // 2. Отправляем через WebSocket
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
    betAmount.value = ''
    autoCashout.value = ''
}

// Lifecycle
onMounted(async () => {
    try {
        await connectToCrashGame()
        await gameStore.loadGameHistory()
    } catch (err) {
        console.error('Failed to initialize crash game:', err)
    }
})

// Watch for game phase changes
watch(() => gameState.value.phase, (newPhase) => {
    if (newPhase === 'finished') {
        setTimeout(prepareNewGame, 5000)
    }
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
  height: 350px;
  border: 1px solid #4479D98A;
  margin: 20px 0px 20px 2.5%;

}

.multiplier-display {
  font-size: 2.5em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  color: #ffffff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.76);
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

</style>
