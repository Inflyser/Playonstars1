<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>⚙️ Панель управления игрой</h1>
      <button @click="logout" class="logout-btn">Выйти</button>
    </div>

    <div class="admin-content">
      <!-- Статистика -->
      <div class="stats-section">
        <h2>📊 Статистика</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-value">{{ stats.total_games || 0 }}</span>
            <span class="stat-label">Всего игр</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ stats.total_bet || 0 }}</span>
            <span class="stat-label">Общая ставка</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ stats.house_profit || 0 }}</span>
            <span class="stat-label">Прибыль</span>
          </div>
        </div>
      </div>

      <!-- Настройки игры -->
      <div class="settings-section">
        <h2>🎮 Настройки Crash игры</h2>
        
        <div class="settings-form">
          <div class="form-group">
            <label>RTP (Return to Player):</label>
            <input 
              type="number" 
              v-model="settings.crash_rtp" 
              min="0.5" 
              max="0.99" 
              step="0.01"
            >
            <span class="hint">Рекомендуется: 0.85-0.95</span>
          </div>

          <div class="form-group">
            <label>Мин. множитель:</label>
            <input 
              type="number" 
              v-model="settings.crash_min_multiplier" 
              min="1.0" 
              step="0.1"
            >
          </div>

          <div class="form-group">
            <label>Макс. множитель:</label>
            <input 
              type="number" 
              v-model="settings.crash_max_multiplier" 
              min="2.0" 
              step="1.0"
            >
          </div>

          <button @click="saveSettings" class="save-btn">💾 Сохранить настройки</button>
        </div>
      </div>

      <!-- Смена пароля -->
      <div class="password-section">
        <h2>🔒 Смена пароля админа</h2>
        <div class="password-form">
          <input 
            type="password" 
            v-model="password.old" 
            placeholder="Старый пароль"
            class="password-input"
          >
          <input 
            type="password" 
            v-model="password.new" 
            placeholder="Новый пароль"
            class="password-input"
          >
          <button @click="changePassword" class="password-btn">🔄 Сменить пароль</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()

const stats = ref({
  total_games: 0,
  total_bet: 0,
  house_profit: 0
})

const settings = ref({
  crash_rtp: 0.95,
  crash_min_multiplier: 1.1,
  crash_max_multiplier: 100.0
})

const password = ref({
  old: '',
  new: ''
})

// Загрузка данных при монтировании
onMounted(async () => {
  await loadStats()
  await loadSettings()
})

// Загрузка статистики
const loadStats = async () => {
  try {
    const response = await api.get('/admin/simple-stats')
    stats.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

// Загрузка настроек
const loadSettings = async () => {
  try {
    const response = await api.get('/admin/crash-settings')
    settings.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки настроек:', error)
  }
}

// Сохранение настроек
const saveSettings = async () => {
  try {
    await api.post('/admin/update-settings', {
      settings: settings.value
    })
    alert('✅ Настройки успешно сохранены!')
  } catch (error) {
    console.error('Ошибка сохранения настроек:', error)
    alert('❌ Ошибка сохранения настроек')
  }
}

// Смена пароля
const changePassword = async () => {
  if (!password.value.old || !password.value.new) {
    alert('⚠️ Заполните все поля пароля')
    return
  }

  if (password.value.new.length < 4) {
    alert('⚠️ Новый пароль слишком короткий')
    return
  }

  try {
    await api.post('/admin/change-password', password.value)
    alert('✅ Пароль успешно изменен!')
    password.value = { old: '', new: '' }
  } catch (error) {
    console.error('Ошибка смены пароля:', error)
    alert('❌ Ошибка смены пароля')
  }
}

// Выход из админки
const logout = () => {
  localStorage.removeItem('admin_token')
  router.push('/')
}
</script>

<style scoped>
.admin-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #2a2642;
}

.logout-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #2a2642, #1a172e);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #00a6fc;
}

.stat-label {
  color: #6a717b;
  font-size: 14px;
}

.settings-section, .password-section {
  background: #1a172e;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #ffffff;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #2a2642;
  border-radius: 8px;
  background: #0f0e1a;
  color: white;
}

.hint {
  font-size: 12px;
  color: #6a717b;
}

.save-btn, .password-btn {
  background: linear-gradient(135deg, #00a6fc, #0088cc);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
}

.password-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #2a2642;
  border-radius: 8px;
  background: #0f0e1a;
  color: white;
}
</style>