<template>
  <div class="crash-game">
    <div class="multiplier-display">
      <h2>{{ currentMultiplier.toFixed(2) }}x</h2>
      <div v-if="isRunning" class="graph">📈</div>
    </div>

    <div class="bet-section">
      <input 
        v-model.number="betAmount" 
        type="number" 
        min="10" 
        :disabled="isRunning"
      >
      <TGButton 
        @click="placeBet" 
        :disabled="isRunning || betAmount <= 0"
      >
        {{ isRunning ? 'Игра идет...' : 'Поставить' }}
      </TGButton>
    </div>

    <div class="history">
      <h3>История игр</h3>
      <div v-for="game in gameHistory" :key="game.id" class="history-item">
        Множитель: {{ game.multiplier }}x
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useApi } from '@/composables/useApi';
import TGButton from '@/components/ui/TGButton.vue';

const { placeCrashBet, getCrashHistory } = useApi();

const currentMultiplier = ref(1.0);
const isRunning = ref(false);
const betAmount = ref(10);
const gameHistory = ref<any[]>([]);

const placeBet = async () => {
  try {
    const result = await placeCrashBet(betAmount.value);
    console.log('Bet placed:', result);
    startGame();
  } catch (error) {
    console.error('Bet error:', error);
  }
};

const startGame = () => {
  isRunning.value = true;
  currentMultiplier.value = 1.0;
  
  const interval = setInterval(() => {
    currentMultiplier.value += 0.1;
    
    if (currentMultiplier.value >= 10) {
      clearInterval(interval);
      endGame();
    }
  }, 100);
};

const endGame = () => {
  isRunning.value = false;
  gameHistory.value.unshift({
    id: Date.now(),
    multiplier: currentMultiplier.value
  });
};

onMounted(async () => {
  gameHistory.value = await getCrashHistory();
});
</script>

<style scoped>
.crash-game {
  padding: 20px;
}

.multiplier-display {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 20px;
}

.bet-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.bet-section input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  flex: 1;
}

.history-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}
</style>