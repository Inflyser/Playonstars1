<template>
  <div class="home">
    <TelegramHeader />



    <BettingPanel />

    <BettingPanel />

    <div class="balance-view">
          <!-- Панель с кнопками -->
      <ButtonTop v-model="selectedPaymentMethod" />

      <!-- Контент в зависимости от выбранного метода -->
      <div class="payment-content">
        <TopAll v-if="selectedPaymentMethod === 'top'" />
        <Top10 v-if="selectedPaymentMethod === 'top10'" />
        <TopMy v-if="selectedPaymentMethod === 'mytop'" />
      </div>
    </div>

    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'

import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'

import ButtonTop from '@/components/layout/ButtonTop.vue'
import Top10 from '@/components/ui/top/Top10.vue'
import TopAll from '@/components/ui/top/TopAll.vue'
import TopMy from '@/components/ui/top/TopMy.vue'

import BettingPanel from '@/components/layout/BettingPanel.vue'


const selectedPaymentMethod = ref('top')
</script>




<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}
</style>