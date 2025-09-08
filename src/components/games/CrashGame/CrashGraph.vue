<template>
  <div class="game-graph">
    <template v-if="phase !== 'finished'">
      <img src="@/assets/images/crashfon.svg" class="graph-background">
      <img src="@/assets/images/kpanel.svg" class="panels-crash">
      <div class="multiplier-display" :class="{ growing: isGameActive }">
        x{{ currentMultiplier.toFixed(2) }}
      </div>
      <canvas ref="graphCanvas" class="graph-canvas"></canvas>
      <img 
        v-if="rocketPosition" 
        :src="rocketImageSrc" 
        class="rocket-overlay"
        :style="rocketStyle"
      >
    </template>

    <div v-else class="game-results">
      <!-- Результаты игры -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, defineProps, withDefaults } from 'vue'
import rocketImageSrc from '@/assets/images/space-monkey-character.svg'

interface Props {
  currentMultiplier: number
  phase: string
  isGameActive: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentMultiplier: 1.0,
  phase: 'waiting',
  isGameActive: false
})

const graphCanvas = ref<HTMLCanvasElement | null>(null)
const graphContext = ref<CanvasRenderingContext2D | null>(null)
const rocketPosition = ref<{x: number; y: number} | null>(null)
const animationFrame = ref<number | null>(null)

const rocketStyle = computed(() => {
  if (!rocketPosition.value) return {}
  return {
    left: rocketPosition.value.x + 'px',
    top: rocketPosition.value.y + 'px'
  }
})


const initGraph = () => {
  if (!graphCanvas.value) return
  
  graphCanvas.value.width = graphCanvas.value.offsetWidth
  graphCanvas.value.height = graphCanvas.value.offsetHeight
  
  graphContext.value = graphCanvas.value.getContext('2d')
  drawGraph()
}

// Функция отрисовки графика
const drawGraph = () => {
  if (!graphContext.value || !graphCanvas.value) return
  
  const ctx = graphContext.value
  const width = graphCanvas.value.width
  const height = graphCanvas.value.height
  
  // Очистка canvas
  ctx.clearRect(0, 0, width, height)
  
  // Параметры графика
  const freezeMultiplier = 2.5
  const freezePointX = width * 0.67
  
  // Вычисляем прогресс
  let progress = currentMultiplier.value / freezeMultiplier
  let renderProgress = Math.min(progress, 1)
  
  // Координаты
  const baseStartY = height * 0.9
  const startY = baseStartY - (baseStartY * 0.3 * renderProgress)
  const endX = freezePointX * renderProgress
  const endY = startY - (startY * renderProgress * renderProgress * 0.7)
  
  // Градиент для области
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0.0, '#534081B2')
  gradient.addColorStop(1.0, '#2C214330')
  
  // Рисуем область под графиком
  ctx.beginPath()
  ctx.fillStyle = gradient
  ctx.moveTo(0, baseStartY)
  
  const points = 20
  for (let i = 1; i <= points; i++) {
    const t = i / points
    const x = endX * t
    const y = startY - (startY * t * t * renderProgress * 0.7)
    ctx.lineTo(x, y)
  }
  
  ctx.lineTo(endX, baseStartY)
  ctx.lineTo(0, baseStartY)
  ctx.closePath()
  ctx.fill()
  
  // Рисуем линию графика
  ctx.beginPath()
  ctx.lineWidth = 2
  ctx.strokeStyle = '#534081'
  ctx.moveTo(0, startY)
  
  for (let i = 1; i <= points; i++) {
    const t = i / points
    const x = endX * t
    const y = startY - (startY * t * t * renderProgress * 0.7)
    ctx.lineTo(x, y)
  }
  
  ctx.stroke()
  
  // Обновляем позицию ракеты
  updateRocketPosition(endX, endY)
  
  // Продолжаем анимацию если игра активна
  if (isGameActive.value) {
    animationFrame.value = requestAnimationFrame(drawGraph)
  }
}

// Функция обновления позиции ракеты
const updateRocketPosition = (endX: number, endY: number) => {
  if (!graphCanvas.value) return
  
  const canvasRect = graphCanvas.value.getBoundingClientRect()
  const scrollX = window.scrollX || window.pageXOffset
  const scrollY = window.scrollY-160 || window.pageYOffset
  
  rocketPosition.value = {
    x: canvasRect.left + endX + scrollX,
    y: canvasRect.top + endY + scrollY + 10
  }
}


// Watchers и lifecycle hooks
watch(() => props.currentMultiplier, () => {
  if (props.isGameActive && !animationFrame.value) {
    animationFrame.value = requestAnimationFrame(drawGraph)
  }
})

watch(() => props.phase, (newPhase) => {
  if (newPhase === 'waiting' || newPhase === 'betting') {
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
      animationFrame.value = null
    }
    rocketPosition.value = null
    drawGraph()
  }
})

onMounted(() => {
  initGraph()
})

defineExpose({
  initGraph,
  drawGraph
})
</script>