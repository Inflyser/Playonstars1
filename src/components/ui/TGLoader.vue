<template>
  <div class="tg-loader">
    <div class="loader-spinner"></div>
    <p class="loader-text">Loading...</p>
  </div>
</template>

<script setup lang="ts">
// Компонент загрузки
</script>

<style scoped>
.tg-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loader-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--tg-theme-secondary-bg-color, #f0f0f0);
  border-top: 4px solid var(--tg-theme-button-color, #007aff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loader-text {
  margin-top: 1rem;
  color: var(--tg-theme-text-color, #000000);
  font-size: 0.875rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>