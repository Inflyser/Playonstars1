<template>
  <div class="betting-container">
    <!-- Первый блок: настройки ставки -->
    <div class="bet-settings">
      <!-- Автоставка -->
      <div class="setting-item">
        <button 
          class="toggle-btn" 
          :class="{ active: autoBet }"
          @click="autoBet = !autoBet"
        >
          <span class="checkmark">✓</span>
        </button>
        <span class="setting-label">{{ $t('auto_stavka') }}</span>
      </div>

      <!-- Быстрая ставка -->
      <div class="setting-item">
        <button 
          class="toggle-btn" 
          :class="{ active: quickBet }"
          @click="quickBet = !quickBet"
        >
          <span class="checkmark">✓</span>
        </button>
        <span class="setting-label">{{ $t('auto_weivod') }}</span>
      </div>

      <!-- Коэффициент -->
      <div class="coefficient-input">
        <input
          v-model="coefficient"
          type="text"
          class="coef-input"
          placeholder="1.00"
          @input="formatCoefficient"
          @blur="validateCoefficient"
        />
        <span class="coef-label">x</span>
      </div>
    </div>

    <!-- Второй блок: управление суммой ставки -->
    <div class="bet-amount-control">
      
      <!-- Левая часть: сумма и быстрые кнопки -->
      <div class="amount-section">
        <div class="amount-main">
          <div class="amount-display">
            <button class="amount-btn minus" @click="decreaseAmount">-</button>
            <div class="amount-value">{{ betAmount }}</div>
            <button class="amount-btn plus" @click="increaseAmount">+</button>
          </div>
        </div>
        <div class="divider"></div>

        <div class="quick-buttons">
          <button 
            v-for="quickAmount in quickAmounts" 
            :key="quickAmount"
            class="quick-btn"
            @click="addToBet(quickAmount)"
          >
            +{{ quickAmount }}
          </button>
          <!-- Добавляем кнопку MAX -->
          <button 
            class="quick-btn max-btn"
            @click="setMaxAmount"
          >
            MAX
          </button>
        </div>
      </div>

      <!-- Правая часть: кнопка ставки -->
      <button 
        :class="buttonConfig.class"
        @click="placeBet"
        :disabled="buttonConfig.disabled"
      >
        <span class="shine-effect" :class="{ red: gamePhase === 'flying' }"></span>
        {{ buttonConfig.text }}
        <div class="divider-bet" :class="{ red: gamePhase === 'flying' }"></div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineProps, defineEmits } from 'vue'

// Props
const props = defineProps({
  betAmount: {
    type: Number,
    default: 100
  },
  maxAmount: {
    type: Number,
    default: 1000
  },
  gamePhase: { // ✅ Добавляем prop для фазы игры
    type: String as () => 'betting' | 'flying' | 'finished',
    default: 'betting'
  },
  currentMultiplier: { // ✅ Текущий множитель для режима полета
    type: Number,
    default: 1.0
  }
})

// Emits
const emit = defineEmits(['update:betAmount', 'place-bet', 'cash-out'])

// Состояния для первого блока
const autoBet = ref(false)
const quickBet = ref(false)
const coefficient = ref('1.0')

// Локальная копия betAmount
const localBetAmount = ref(props.betAmount)

// Следим за изменениями извне
watch(() => props.betAmount, (newVal) => {
  localBetAmount.value = newVal
})

// Следим за локальными изменениями
watch(localBetAmount, (newVal) => {
  emit('update:betAmount', newVal)
})

// Computed свойства
const isDisabled = computed(() => {
  return localBetAmount.value <= 0 || localBetAmount.value > props.maxAmount
})

const quickAmounts = computed(() => {
  // Динамические быстрые суммы на основе макс. суммы
  const max = props.maxAmount
  return [
    Math.floor(max * 0.1),
    Math.floor(max * 0.25), 
    Math.floor(max * 0.5),
    Math.floor(max * 0.75)
  ].filter(amount => amount > 0)
})

// Методы
const setMaxAmount = () => {
  localBetAmount.value = props.maxAmount
}

const increaseAmount = () => {
  const newAmount = localBetAmount.value + 10
  if (newAmount <= props.maxAmount) {
    localBetAmount.value = newAmount
  } else {
    localBetAmount.value = props.maxAmount
  }
}

const decreaseAmount = () => {
  if (localBetAmount.value > 10) {
    localBetAmount.value -= 10
  }
}

const addToBet = (amount: number) => {
  const newAmount = localBetAmount.value + amount
  if (newAmount <= props.maxAmount) {
    localBetAmount.value = newAmount
  } else {
    localBetAmount.value = props.maxAmount
  }
}


// Computed свойство для определения текста и стиля кнопки
const buttonConfig = computed(() => {
  if (props.gamePhase === 'flying') {
    return {
      text: `${$t('button_stavka2')} x${props.currentMultiplier.toFixed(2)}`,
      class: 'cashout-btn', // Красный стиль
      disabled: false
    }
  }
  
  return {
    text: `${$t('button_stavka1')}`,
    class: 'place-bet-btn', // Зеленый стиль
    disabled: isDisabled.value
  }
})

// Обновляем метод placeBet
const placeBet = () => {
  if (props.gamePhase === 'flying') {
    // Режим "Забрать ставку"
    emit('cash-out') // ✅ Новое событие для вывода
  } else {
    // Режим обычной ставки
    if (!isDisabled.value) {
      emit('place-bet', {
        amount: localBetAmount.value,
        coefficient: coefficient.value,
        autoBet: autoBet.value,
        quickBet: quickBet.value
      })
    }
  }
}

// Форматирование коэффициента (остается без изменений)
const formatCoefficient = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value = target.value
  
  value = value.replace(',', '.')
  value = value.replace(/[^\d.]/g, '')
  
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('')
  }
  
  if (parts.length === 2) {
    value = parts[0] + '.' + parts[1].slice(0, 2)
  }
  
  target.value = value
  coefficient.value = value
}

const validateCoefficient = () => {
  if (!coefficient.value) {
    coefficient.value = '1.00'
    return
  }
  
  let value = coefficient.value
  
  if (!value.includes('.')) {
    value += '.00'
  }
  
  const parts = value.split('.')
  if (parts.length === 1) {
    value += '.00'
  } else if (parts[1].length === 1) {
    value += '0'
  } else if (parts[1].length === 0) {
    value += '00'
  }
  
  const numValue = parseFloat(value)
  if (numValue < 1.00) {
    value = '1.00'
  }
  
  coefficient.value = value
}
</script>

<style scoped>
.betting-container {
  margin: 20px 0px 20px 2.5%;
  width: 95%;
  background: #1D1131;
  border: 1.5px solid #25213C;
  border-radius: 16px;
}

/* Первый блок: настройки ставки */
.bet-settings {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-btn {
  width: 20px;
  height: 20px;
  border: 2px solid #534081B2;
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: #534081B2
}

.toggle-btn.active .checkmark {
  opacity: 1;
}

.checkmark {
  color: white;
  font-size: 12px;
  font-weight: bold;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.setting-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  font-weight: 500;
  margin: 0px 15px 0px 0px;
}

.coefficient-input {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  position: relative;
}

.coef-input {
  width: 70px; /* Немного шире для двух знаков */
  padding: 6px 20px 6px 8px; /* Правое padding для символа x */
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #2A2642;
  border-radius: 6px;
  color: white;
  text-align: center;
  font-size: 12px;
  /* Убираем стрелочки */
  -moz-appearance: textfield;
}

.coef-input::-webkit-outer-spin-button,
.coef-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.coef-input:focus {
  outline: none;
  border-color: #00A6FC;
}

.coef-label {
  position: absolute;
  right: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  pointer-events: none; /* Чтобы не мешало кликам */
}

/* Второй блок: управление суммой ставки */
.bet-amount-control {
  position: relative;
  background-color: #261740;
  display: flex;
  align-items: flex-start;
  border-radius: 20px 20px 15px 15px;
  padding: 15px;
  gap: 20px;
  margin: 15px -15px -15px -15px;
}

.divider-bet {
  width: 40%;
  height: 2.5px;
  border-radius: 5px;
  background: linear-gradient(135deg, #ADE134, #579C27);
  position: absolute;
  top: 99px;
}

.amount-section {
  background-color: #2C2143;
  padding: 8px;
  border-radius: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.amount-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.amount-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 500;
}

.amount-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.amount-btn {
  width: 28px;
  height: 26px;
  border: none;
  border-radius: 8px;
  font-size: 20px;
  background: #534081B2;;
  color: #F0F0F080;
  cursor: pointer;
  transition: all 0.2s ease;
}

.amount-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.amount-value {
  font-weight: bold;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  min-width: 75px;
  text-align: center;
}

.quick-buttons {
  display: flex;
  gap: 2px;
}

.quick-btn {
  background: #534081B2;
  border: 1px solid #2A2642;
  border-radius: 6px;
  color: #F0F0F080;
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: white;
}

.place-bet-btn {
  position: relative;
  padding: 10px 12px;
  background: linear-gradient(135deg, #ADE134, #579C27);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: center;
}

.place-bet-btn:hover {
  background: linear-gradient(135deg, #89b32a, #44791e);
  transform: translateY(-2px);
}


.divider {
  width: 100%;
  height: 1px;
  background: #F0F0F01A;
}

.shine-effect {
  position: absolute;
  top: 4px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.6) 10%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 70%
  );
  border-radius: 50%;
  transform: translate(-30%, -30%);
  pointer-events: none;
  filter: blur(2px);
  box-shadow: 
    0 0 10px rgba(255, 255, 255, 0.5),
    0 0 20px rgba(255, 255, 255, 0.3);
}

/* Красная кнопка для вывода */
.cashout-btn {
  position: relative;
  padding: 10px 12px;
  background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cashout-btn:hover {
  background: linear-gradient(135deg, #e05a5a, #c44a4a) !important;
  transform: translateY(-2px);
}

/* Красный shine эффект */
.shine-effect.red {
  background: radial-gradient(
    circle at center,
    rgba(255, 200, 200, 0.8) 10%,
    rgba(255, 150, 150, 0.5) 50%,
    transparent 70%
  ) !important;
  box-shadow: 
    0 0 10px rgba(255, 100, 100, 0.6),
    0 0 20px rgba(255, 100, 100, 0.4) !important;
}

/* Красный divider */
.divider-bet.red {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
}

/* Анимация пульсации для кнопки вывода */


/* Адаптивность */

@media (max-width: 768px) {
  .amount-value {
    min-width: 70%;
    text-align: center;
  }
  
  .bet-settings {
    flex-wrap: wrap;
    gap: 12px;
  }
  .betting-container {
    padding: 16px;
  }
  
  .coefficient-input {
    margin-left: 0;
    margin-right: auto;
  }
  
  .bet-amount-control {
    flex-direction: row; /* ← Оставляем row вместо column */
    align-items: stretch; /* ← Добавляем */
    gap: 16px;
  }

  
  .amount-section {
    flex: 1;
  }
  
  .quick-buttons {
    flex-wrap: wrap;
    gap: 4px; /* ← Уменьшаем gap между кнопками */
  }
  
  .quick-btn {
    padding: 5px 6px; /* ← Уменьшаем padding */
    font-size: 10px;
    flex: 1;
 
  }

  
  .cashout-btn {
    width: auto; /* ← Убираем width: 100% */
    height: 100%; /* ← Оставляем */
    padding: 26px 55px; /* ← Корректируем padding */
    min-width: 80px; /* ← Добавляем минимальную ширину */
  }
  
  .place-bet-btn {
    width: auto; /* ← Убираем width: 100% */
    height: 100%; /* ← Оставляем */
    padding: 26px 55px; /* ← Корректируем padding */
    min-width: 80px; /* ← Добавляем минимальную ширину */
  }

}

@media (max-width: 480px) {
  .amount-value {
    min-width: 70px;
    text-align: center;
  }
  .betting-container {
    padding: 16px;
  }
  
  .bet-settings {
    gap: 8px;
  }
  
  .setting-label {
    font-size: 11px;
  }
  
  .coef-input {
    width: 50px;
    font-size: 11px;
  }
  
  .bet-amount-control {
    flex-direction: row; /* ← Оставляем row */
    gap: 12px; /* ← Уменьшаем gap */
  }
  
  .quick-buttons {
    flex-wrap: wrap;
    gap: 4px; /* ← Уменьшаем gap между кнопками */
  }
  
  .quick-btn {
    padding: 5px 6px; /* ← Уменьшаем padding */
    font-size: 10px;
    flex: 1;
    min-width: 15px; /* ← Добавляем минимальную ширину */
  }
  
  .place-bet-btn {
    padding: 30px 75px; /* ← Корректируем padding */
    font-size: 16px; /* ← Уменьшаем шрифт */
    min-width: 70px; /* ← Минимальная ширина */
    white-space: nowrap; /* ← Запрещаем перенос текста */
    height: 100%;
  }

  .cashout-btn {
    padding: 30px 75px; /* ← Корректируем padding */
    font-size: 16px; /* ← Уменьшаем шрифт */
    min-width: 70px; /* ← Минимальная ширина */
    white-space: nowrap; /* ← Запрещаем перенос текста */
    height: 100%;
  }
}

/* Добавляем дополнительный медиа-запрос для очень маленьких экранов */
@media (max-width: 360px) {
  .bet-amount-control {
    flex-direction: column; /* ← Только на очень маленьких переходим на колонку */
    gap: 12px;
  }
  
  .place-bet-btn {
    width: 100%;
    height: auto;
  }

  .cashout-btn {
    width: 100%;
    height: auto;
  }
  
  .quick-buttons {
    justify-content: center;
  }
}

/* Для мобильных устройств */
@media (max-width: 480px) {
  .cashout-btn {
    padding: 30px 75px;
    font-size: 14px; /* Чуть меньше шрифт для длинного текста */
    min-width: 70px;
  }
}
</style>