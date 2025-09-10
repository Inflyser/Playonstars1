<template>
  <div class="login-container">
    <div class="login-form">
      <h2>🔐 Вход в админку</h2>
      
      <input 
        type="password" 
        v-model="password" 
        placeholder="Введите пароль админа"
        @keyup.enter="login"
        class="login-input"
      >
      
      <button @click="login" class="login-btn">Войти</button>
      
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()
const password = ref('')
const error = ref('')

const login = async () => {
  if (!password.value) {
    error.value = 'Введите пароль'
    return
  }

  try {
    const response = await api.post('/admin/login', {
      password: password.value
    })
    
    if (response.data.status === 'success') {
      localStorage.setItem('admin_token', 'authenticated')
      router.push('/admin')
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Ошибка входа'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0e1a, #1a172e);
}

.login-form {
  background: #2a2642;
  padding: 40px;
  border-radius: 16px;
  text-align: center;
  width: 300px;
}

.login-input {
  width: 100%;
  padding: 12px;
  margin: 15px 0;
  border: 1px solid #3a354d;
  border-radius: 8px;
  background: #1a172e;
  color: white;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #00a6fc, #0088cc);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.error-message {
  color: #ff4757;
  margin-top: 15px;
}
</style>