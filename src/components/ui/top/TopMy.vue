<template>
  <div class="top-my">
    <div class="placeholder">
      <img src="@/assets/images/coin.svg" alt="Star" class="placeholder-icon" />
      <h3>Мой топ</h3>
      <p>Функция в разработке</p>
    </div>
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped>
.top-my {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.placeholder {
  text-align: center;
  color: var(--tg-theme-hint-color, #888888);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  opacity: 0.5;
}

h3 {
  margin-bottom: 0.5rem;
  color: var(--tg-theme-text-color, #ffffff);
}

p {
  color: var(--tg-theme-hint-color, #888888);
}
</style>