<template>
  <div class="home">




    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import BottomNavigation from '@/components/layout/BottomNavigation.vue'

</script>



<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}
</style>