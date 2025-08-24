<template>
  <div class="home">
    <TelegramHeader />
    <TelegramHeader2 />

    <div class="balance-view">
      
      <!-- Панель с кнопками -->
      <ButtonGroup v-model="selectedPaymentMethod" />
      
      <!-- Контент в зависимости от выбранного метода -->
      <div class="payment-content">
        <TonPayment v-if="selectedPaymentMethod === 'ton'" />
        <StarsPayment v-if="selectedPaymentMethod === 'stars'" />
        <GiftsPayment v-if="selectedPaymentMethod === 'gifts'" />
      </div>
    </div>

    <button @click="$router.back()">Назад</button>




    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'



import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'

import ButtonGroup from '@/components/layout/ButtonGroup.vue'
import TonPayment from '@/components/ui/balance/TonPayment.vue'
import StarsPayment from '@/components/ui/balance/StarsPayment.vue'
import GiftsPayment from '@/components/ui/balance/GiftsPayment.vue'


const selectedPaymentMethod = ref('ton')
</script>


<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}
</style>

