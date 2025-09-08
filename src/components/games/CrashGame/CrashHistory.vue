<template>
  <div class="game-history">
    <div class="history-list">
      <div
        v-for="(game, index) in history" 
        :key="index"
        class="history-item"
        :class="getHistoryClass(game.multiplier)"
      >
        {{ game.multiplier.toFixed(2) }}x
      </div>
    </div>

    <div class="history-scroll-indicator">
      <div class="indicator-icon">
        <img src="@/assets/images/clock.svg" alt="scroll">
      </div>
      <div class="indicator-shadow"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, computed } from 'vue'

interface CrashGameHistory {
  gameId: number
  multiplier: number
  crashedAt: number
  timestamp: string
  playersCount: number
  totalBet: number
  totalPayout: number
}

interface Props {
  history: CrashGameHistory[]
}

const props = defineProps<Props>()

const getHistoryClass = (multiplier: number) => {
  if (multiplier < 2) return 'multiplier-low'
  if (multiplier >= 2 && multiplier < 7) return 'multiplier-medium'
  if (multiplier >= 7) return 'multiplier-high'
  return 'multiplier-low'
}
</script>

<style scoped>

.game-history {
  position: relative;
  width: 95%;
  margin: 8px 0px 15px 2.5%;
  border-bottom: 1px solid #25213C;
  overflow-x: auto;
  white-space: nowrap;
  padding-bottom: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.game-history::-webkit-scrollbar {
  display: none;
}

.history-list {
  display: inline-flex;
  gap: 4px;
  padding: 5px 45px 5px 5px; /* Увеличили отступ справа для панельки */
}

.history-scroll-indicator {
  position: absolute;
  right: 3.5px;
  top: 35%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  z-index: 10;
  pointer-events: none;
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
  z-index: 2;
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
</style>