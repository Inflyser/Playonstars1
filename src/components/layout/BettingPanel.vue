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
        <span class="setting-label">Авто ставка</span>
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
        <span class="setting-label">Авто вывод</span>
      </div>

      <!-- Коэффициент -->
      <div class="coefficient-input">
        <input
          v-model="coefficient"
          type="number"
          step="0.1"
          min="1.0"
          class="coef-input"
          placeholder="1.0"
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
        </div>
      </div>

      <!-- Правая часть: кнопка ставки -->
      
      <button class="place-bet-btn" @click="placeBet">
        СТАВКА
      </button>
    
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Состояния для первого блока
const autoBet = ref(false)
const quickBet = ref(false)
const coefficient = ref('1.0')

// Состояния для второго блока
const betAmount = ref(100)
const quickAmounts = [50, 100, 200, 500]

// Увеличение суммы ставки
const increaseAmount = () => {
  betAmount.value += 10
}

// Уменьшение суммы ставки
const decreaseAmount = () => {
  if (betAmount.value > 10) {
    betAmount.value -= 10
  }
}

// Быстрое добавление к ставке
const addToBet = (amount: number) => {
  betAmount.value += amount
}

// Размещение ставки
const placeBet = () => {
  console.log('Ставка размещена:', {
    amount: betAmount.value,
    coefficient: coefficient.value,
    autoBet: autoBet.value,
    quickBet: quickBet.value
  })
  // Здесь будет логика отправки ставки
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
  gap: 8px;
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
}

.coefficient-input {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.coef-input {
  width: 60px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #2A2642;
  border-radius: 6px;
  color: white;
  text-align: center;
  font-size: 12px;
}

.coef-input:focus {
  outline: none;
  border-color: #00A6FC;
}

.coef-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

/* Второй блок: управление суммой ставки */
.bet-amount-control {
  background-color: #261740;
  display: flex;
  align-items: flex-start;
  border-radius: 20px 20px 15px 15px;
  padding: 15px;
  gap: 20px;
  margin: 15px -15px -15px -15px;
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
  
  .quick-buttons {
    justify-content: center;
  }
}
</style>