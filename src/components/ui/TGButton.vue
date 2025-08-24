<template>
<button class="mini-button" @click="navigateToBalance">
  <img src="@/assets/images/plus-small.svg" alt="Добавить" />
</button>
<button class="mini-button" @click="navigateToBalance">
  <img src="@/assets/images/refresh-small.svg" alt="Обновить" />
</button>
          
</template>

<script setup lang="ts">

import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToBalance = () => {
  router.push('/balance')
}

</script>



<style scoped>
.mini-button {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 6px;
  width: 16px;
  height: 0px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mini-button:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.mini-button img {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

</style>