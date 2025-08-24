<template>
  <div class="button-group">
    <button
      v-for="button in buttons"
      :key="button.id"
      :class="['group-button', { active: activeButton === button.id }]"
      @click="selectButton(button.id)"
    >
      <span class="button-label">{{ button.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue: string // Обязательный пропс
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Тип для кнопок
interface GroupButton {
  id: string
  label: string
}

const buttons: GroupButton[] = [
  { id: 'ton', label: 'Ton' },
  { id: 'stars', label: 'Звезды' },
  { id: 'gifts', label: 'Подарки' }
]

// Используем переданное значение из v-model
const activeButton = ref(props.modelValue)

// Синхронизируем изменения
watch(activeButton, (newValue) => {
  emit('update:modelValue', newValue)
})

// Обработчик клика
const selectButton = (buttonId: string): void => {
  activeButton.value = buttonId
}
</script>

<style scoped>
.button-group {
  display: flex;
  width: 95%;
  background: #100D1F;
  border-radius: 15px;
  padding: 4px;
  gap: 2px;
  margin: 0px 0px 20px 2.5%;

}

.group-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;
}


.group-button.active {
  background: #241D49;
  color: white;
}

.button-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.button-label {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

/* Адаптивность */
@media (max-width: 480px) {
  .button-group {
    padding: 3px;
    gap: 1px;
  }
  
  .group-button {
    padding: 10px 12px;
    gap: 6px;
  }
  
  .button-icon {
    width: 18px;
    height: 18px;
  }
  
  .button-label {
    font-size: 12px;
  }
}
</style>