<template>
  <div>
    <div>Баланс: {{ balance }}</div>
    <button @click="refreshBalance">Обновить</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApi } from '@/composables/useApi';

const { getProfile } = useApi();
const balance = ref(0);

const refreshBalance = async () => {
  const profile = await getProfile();
  balance.value = profile.balance; // Напрямую из API!
};
</script>