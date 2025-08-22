<template>
  <button 
    :class="['tg-button', size, { disabled }]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<style scoped>
.tg-button {
  background: var(--tg-theme-button-color, #40a7e3);
  color: var(--tg-theme-button-text-color, #ffffff);
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.tg-button:hover:not(.disabled) {
  opacity: 0.9;
}

.tg-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tg-button.small {
  padding: 8px 16px;
  font-size: 14px;
}

.tg-button.large {
  padding: 16px 24px;
  font-size: 18px;
}
</style>