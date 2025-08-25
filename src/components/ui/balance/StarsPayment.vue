<template>

    <InputPanel
      :prefix-text="'STARS'"
      :placeholder="'Введите сумму в STARS'"
      :max-value="'5000'"
      :icon-type="'stars'"
    />

    <p style="color: #6A717B;  font-size: 13px; margin: -10px 10px 15px 20px;">
        Минимальная сумма: 100 STARS
    </p>
    
    <div class="two-buttons-container">
      <button class="btn primary" @click="$router.back()">Отмена</button>
      <button class="btn secondary">Пополнить</button>
    </div>
    
    
</template>

<script setup lang="ts">
import InputPanel from '@/components/layout/InputPanel.vue'
</script>

<style scoped>

.two-buttons-container {
  display: flex;
  gap: 12px;
  padding: 0 15px 15px 15px;
}

.btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.secondary {
  background: linear-gradient(135deg, #00A6FC, #0088CC);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid #2A2642;
}

</style>