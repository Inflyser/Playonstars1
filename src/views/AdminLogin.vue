<template>
  <div class="login-container">
    <div class="login-form">
      <h1>🔐 Вход в админку</h1>
      <input 
        type="password" 
        v-model="password" 
        placeholder="Введите пароль админа"
        @keyup.enter="login"
        class="password-input"
      >
      <button @click="login" class="login-btn">Войти</button>
      <p class="hint">Используйте команду /admin пароль в боте</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()
const password = ref('')

const login = async () => {
  if (!password.value) {
    alert('Введите пароль')
    return
  }

  try {
    const response = await api.post('/admin/login', { password: password.value })
    localStorage.setItem('admin_token', 'authenticated')
    router.push('/admin')
  } catch (error) {
    alert('Неверный пароль админа')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
}

.login-form {
  background: #1a172e;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  width: 300px;
}

.password-input {
  width: 100%;
  padding: 12px;
  margin: 15px 0;
  border: 1px solid #2a2642;
  border-radius: 8px;
  background: #0f0e1a;
  color: white;
}

.login-btn {
  background: linear-gradient(135deg, #00a6fc, #0088cc);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
}

.hint {
  margin-top: 15px;
  color: #6a717b;
  font-size: 12px;
}
</style>