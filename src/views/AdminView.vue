<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>⚙️ Панель управления</h1>
      <button @click="logout" class="logout-btn">Выйти</button>
    </div>

    <div class="admin-content">
      <!-- Настройки RTP -->
      <div class="settings-section">
        <h2>🎮 Настройка RTP (Return to Player)</h2>
        <div class="rtp-control">
          <div class="rtp-slider-container">
            <label>Текущее значение: <span class="rtp-value">{{ rtpValue }}</span></label>
            <input 
              type="range" 
              v-model="rtpValue" 
              min="80" 
              max="99" 
              step="1"
              class="rtp-slider"
              @change="updateRTP"
            >
            <div class="rtp-labels">
              <span>0.80</span>
              <span>0.90</span>
              <span>0.99</span>
            </div>
          </div>
          <button @click="updateRTP" class="save-btn">💾 Сохранить RTP</button>
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

      <!-- Запросы на вывод -->
      <div class="withdrawals-section">
        <h2>💸 Запросы на вывод средств</h2>
        <div class="withdrawals-list">
          <div class="empty-state">
            <div class="empty-icon">📭</div>
            <h3>Пока нет запросов на вывод</h3>
            <p>Здесь будут отображаться все запросы на вывод средств от пользователей</p>
          </div>
          
          <!-- Пример будущего запроса (закомментирован) -->
          <!--
          <div class="withdrawal-item">
            <div class="withdrawal-info">
              <span class="user">@username</span>
              <span class="amount">100 TON</span>
              <span class="wallet">EQABC...123</span>
            </div>
            <div class="withdrawal-actions">
              <button class="approve-btn">✅ Одобрить</button>
              <button class="reject-btn">❌ Отклонить</button>
            </div>
          </div>
          -->
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
const password = ref({ old: '', new: '' })
const rtpValue = ref(95) // Значение по умолчанию 0.95

// Загрузка текущих настроек при монтировании
onMounted(async () => {
  await loadSettings()
})

// Загрузка текущих настроек RTP
const loadSettings = async () => {
  try {
    const response = await api.get('/api/admin/settings')
    if (response.data.crash_rtp) {
      // Конвертируем 0.95 в 95 для ползунка
      rtpValue.value = Math.round(response.data.crash_rtp * 100)
    }
  } catch (error) {
    console.error('Ошибка загрузки настроек:', error)
  }
}

// Обновление RTP
const updateRTP = async () => {
  try {
    const rtp = rtpValue.value / 100 // Конвертируем 95 в 0.95
    await api.post('/api/admin/update-settings', {
      crash_rtp: rtp
    })
    alert('✅ RTP успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления RTP:', error)
    alert('❌ Ошибка обновления RTP')
  }
}

// Смена пароля
const changePassword = async () => {
  if (!password.value.old || !password.value.new) {
    alert('⚠️ Заполните все поля пароля')
    return
  }

  try {
    await api.post('/admin/change-password', password.value)
    alert('✅ Пароль успешно изменен!')
    password.value = { old: '', new: '' }
  } catch (error) {
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
  max-width: 500px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.logout-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.settings-section {
  background: #1a172e;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.rtp-control {
  margin-bottom: 15px;
}

.rtp-slider-container {
  margin-bottom: 15px;
}

.rtp-value {
  font-weight: bold;
  color: #00a6fc;
  font-size: 18px;
}

.rtp-slider {
  width: 100%;
  height: 8px;
  margin: 15px 0;
  border-radius: 4px;
  background: #2a2642;
  outline: none;
  -webkit-appearance: none;
}

.rtp-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #00a6fc;
  cursor: pointer;
}

.rtp-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #00a6fc;
  cursor: pointer;
  border: none;
}

.rtp-labels {
  display: flex;
  justify-content: space-between;
  color: #6a717b;
  font-size: 12px;
  margin-top: 5px;
}

.save-btn {
  background: linear-gradient(135deg, #00a6fc, #0088cc);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
}

.password-section {
  background: #1a172e;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
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

.password-btn {
  background: linear-gradient(135deg, #00a6fc, #0088cc);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
}

.withdrawals-section {
  background: #1a172e;
  padding: 20px;
  border-radius: 12px;
}

.withdrawals-section h2 {
  margin-bottom: 20px;
  color: #ffffff;
}

.withdrawals-list {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
  color: #6a717b;
}

.empty-icon {
  font-size: 50px;
  margin-bottom: 15px;
}

.empty-state h3 {
  margin: 10px 0;
  color: #ffffff;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
}

/* Стили для будущих запросов на вывод */
.withdrawal-item {
  background: #2a2642;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.withdrawal-info {
  flex: 1;
}

.user {
  display: block;
  font-weight: bold;
  color: #00a6fc;
}

.amount {
  display: block;
  color: #ffffff;
  font-size: 16px;
  margin: 5px 0;
}

.wallet {
  display: block;
  color: #6a717b;
  font-size: 12px;
  font-family: monospace;
}

.withdrawal-actions {
  display: flex;
  gap: 10px;
}

.approve-btn {
  background: #00a6fc;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.reject-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}
</style>