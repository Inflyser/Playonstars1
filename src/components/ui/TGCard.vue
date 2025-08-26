<template>
  <div class="tg-card">
    <h3 v-if="title" class="card-title">{{ title }}</h3>
    <div class="card-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.tg-card {
  background: var(--tg-theme-secondary-bg-color, #f0f0f0);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.card-title {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--tg-theme-text-color, #000000);
}

.card-content {
  color: var(--tg-theme-text-color, #000000);
}
</style>