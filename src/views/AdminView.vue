<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>⚙️ Панель управления</h1>
      <button @click="logout" class="logout-btn">Выйти</button>
    </div>

    <div class="admin-content">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()
const password = ref({ old: '', new: '' })

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
  max-width: 400px;
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

.password-section {
  background: #1a172e;
  padding: 20px;
  border-radius: 12px;
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
</style>