<template>
  <div class="login">
    <div class="login-card">
      <h1>{{ $t('auth.login') }}</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>{{ $t('auth.username') }}</label>
          <input v-model="username" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t('auth.password') }}</label>
          <input v-model="password" type="password" required />
        </div>
        <button type="submit" class="btn btn-primary">
          {{ $t('auth.submit') }}
        </button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  try {
    const response = await axios.post('/api/auth/login', {
      username: username.value,
      password: password.value
    })

    if (response.data.success) {
      localStorage.setItem('user', JSON.stringify(response.data.user))
      router.push('/projects')
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed'
  }
}
</script>

<style scoped>
.login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 56px);
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-card h1 {
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.error {
  color: #f44336;
  text-align: center;
  margin-top: 1rem;
}
</style>
