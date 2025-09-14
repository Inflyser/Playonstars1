<template>
  <div>
    <div class="icon-wrapper">
      <div class="circle-icon-container">
        <img src="@/assets/images/gift.svg" alt="Иконка" class="circle-icon" />
      </div>
    </div>
    <h3 style="text-align: center; color: white;">{{ t('gift') }}</h3>
    <p style="color: #A2A2A2; text-align: center; font-size: 14px; margin: 10px 20px 40px 20px;">{{ t('gift1') }}</p>
    

    <div class="two-buttons-container">
      <button class="btn primary" @click="$router.back()">{{ t('balance_but1') }}</button>
      <button class="btn secondary">{{ t('balance_but2') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">


import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
</script>

<style scoped>
.icon-wrapper {
  margin: 40px 0px 0px 0px;
  display: flex;
  justify-content: center; /* Центрирование по горизонтали */
  align-items: center;     /* Центрирование по вертикали */
  width: 100%;
  height: 100%;            /* Занимает всю высоту родителя */
}

.circle-icon {
  width: 70px;
  height: 70px;
  object-fit: contain;
}



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