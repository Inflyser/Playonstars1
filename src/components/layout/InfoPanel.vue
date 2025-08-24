<template>
  <div class="info-panel">
    <!-- 1. Текст названия -->
    <h3 class="panel-title">{{ title }}</h3>

    <!-- 2. Иконка SVG + текст -->
    <div class="icon-text-row">
      <img src="@/assets/images/gameicon.svg" class="panel-icon" />
      <span class="icon-text">{{ iconText }}</span>
    </div>

    <!-- 3. Текст | текст (разделенные линией) -->
    <div class="text-divider-row">
      <span class="left-text">{{ leftText }}</span>
      <span class="right-text">{{ rightText }}</span>
    </div>

    <!-- 4. Прогрессбар -->
    <div class="progress-container">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progress + '%' }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Импортируем SVG иконки
import { defineProps } from 'vue'

defineProps({
  title: {
    type: String,
    default: 'Название панели'
  },
  iconText: {
    type: String,
    default: 'Текст с иконкой'
  },
  leftText: {
    type: String,
    default: 'Левый текст'
  },
  rightText: {
    type: String,
    default: 'Правый текст'
  },
  progress: {
    type: Number,
    default: 50,
    validator: (value: number) => value >= 0 && value <= 100
  }
})
</script>

<style scoped>
.info-panel {
  margin: 10px;
  background: #009AFE;
  border-radius: 16px;
  padding: 20px;
  width: 95%;
  max-width: 400px;
}

/* 1. Текст названия */
.panel-title {
  color: white;
  font-size: 26px;
  font-weight: bold;
  margin: 0;
}

/* 2. Иконка SVG + текст */
.icon-text-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0px 5px 0px;
  border-radius: 10px;
  border: none;
  margin: 0;
}

.panel-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  border: none;
}

.icon-text {
  color: white;
  font-size: 16px;
  
}

/* 3. Текст | текст */
.text-divider-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  border-radius: 10px;
}

.left-text,
.right-text {
  color: white;
  font-size: 16px;
  flex: 1;
}

.left-text {
  margin: 5px 5px -15px -10px;
  font-weight: 500;
}

.right-text {
  margin: 5px 5px -15px -10px;
  text-align: right;
  font-weight: 700;
}



/* 4. Прогрессбар */
.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;

}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Адаптивность */
@media (max-width: 480px) {
  .info-panel {
    padding: 16px;
    max-width: 95%;
  }
  
  .panel-title {
    font-size: 20px;
  }
  
  .icon-text {
    font-size: 14px;
  }
  
  .left-text,
  .right-text {
    font-size: 16px;
  }
  
  .progress-text {
    font-size: 13px;
  }
}
</style>