<template>
  <div 
    class="input-panel" 
    :class="{ focused: isFocused }"
    @click="focusInput"
  >
    <!-- Левая часть: иконка и текст -->
    <div class="input-prefix">
      <img :src="getIconUrl" :alt="prefixText" class="prefix-icon" />
      <span class="prefix-text">{{ prefixText }}</span>
    </div>

    <!-- Поле ввода -->
    <input
      ref="inputRef"
      type="text"
      :value="modelValue"
      @input="handleInput"
      @focus="isFocused = true"
      @blur="isFocused = false"
      class="custom-input"
      :placeholder="placeholder"
    />

    <!-- Правая часть: кнопка Макс -->
    <button class="max-button" @click="setMaxValue">
      Макс
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Импортируем PNG иконки
import tonIcon from '@/assets/images/ton.svg'
import starsIcon from '@/assets/images/coin.svg'

// Пропсы
interface Props {
  modelValue?: string
  prefixText?: string
  placeholder?: string
  maxValue?: string
  iconType?: 'ton' | 'stars' | string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  prefixText: 'Сумма',
  placeholder: 'Введите сумму...',
  maxValue: '1000',
  iconType: 'ton'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Состояния
const isFocused = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

// Карта иконок
const iconMap = {
  ton: tonIcon,
  stars: starsIcon
} as Record<string, any>

// Получаем URL иконки на основе iconType
const getIconUrl = computed(() => {
  return iconMap[props.iconType?.toLowerCase()] || tonIcon
})

// Обработчик ввода
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

// Установить максимальное значение
const setMaxValue = () => {
  emit('update:modelValue', props.maxValue)
}

// Фокус на инпут при клике на всю панель
const focusInput = () => {
  if (inputRef.value) {
    inputRef.value.focus()
    
    // Очищаем поле при клике, если оно не пустое
    if (props.modelValue && !isFocused.value) {
      emit('update:modelValue', '')
    }
  }
}
</script>

<style scoped>
/* Стили остаются без изменений */
.input-panel {
  width: 95%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid #534081B2;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: text;
  margin: 0px 0px 20px 2.5%;
}

.input-prefix {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.prefix-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.prefix-text {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
}

.custom-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 14px;
  outline: none;
  min-width: 0;
}

.max-button {
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

/* Адаптивность */
@media (max-width: 480px) {
  .input-panel {
    padding: 12px;
    gap: 8px;
  }
  
  .prefix-icon {
    width: 14px;
    height: 14px;
  }
  
  .prefix-text {
    font-size: 12px;
  }
  
  .custom-input {
    font-size: 14px;
  }
  
  .max-button {
    padding: 6px 10px;
    font-size: 11px;
  }
}
</style>