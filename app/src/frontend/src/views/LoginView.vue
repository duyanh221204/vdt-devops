<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth.js'
import { useAuth } from '@/stores/auth.js'

const router = useRouter()
const { fetchUser } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  if (!username.value.trim() || !password.value) {
    errorMsg.value = 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await login(username.value.trim(), password.value)
    const token = res.data?.access_token
    if (!token) throw new Error('Không nhận được token từ server.')

    localStorage.setItem('access_token', token)
    await fetchUser()
    router.push({ name: 'Home' })
  } catch (err) {
    const status = err.response?.status
    if (status === 401 || status === 400) {
      errorMsg.value = 'Sai tên đăng nhập hoặc mật khẩu.'
    } else {
      errorMsg.value = 'Đã xảy ra lỗi. Vui lòng thử lại sau.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- Left panel (decorative) -->
    <div class="login-left" aria-hidden="true">
      <div class="login-left-content">
        <div class="brand-icon-lg">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <h1>Student Management</h1>
        <p>Hệ thống quản lý sinh viên hiện đại, đơn giản và hiệu quả.</p>
        <div class="login-illustration">
          <svg width="260" height="200" viewBox="0 0 260 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="20" y="120" width="220" height="60" rx="10" fill="rgba(255,255,255,0.08)"/>
            <rect x="36" y="136" width="120" height="10" rx="4" fill="rgba(255,255,255,0.25)"/>
            <rect x="36" y="154" width="80" height="8" rx="4" fill="rgba(255,255,255,0.15)"/>
            <circle cx="210" cy="150" r="14" fill="rgba(255,255,255,0.12)"/>
            <rect x="20" y="50" width="220" height="60" rx="10" fill="rgba(255,255,255,0.05)"/>
            <rect x="36" y="66" width="100" height="10" rx="4" fill="rgba(255,255,255,0.18)"/>
            <rect x="36" y="84" width="60" height="8" rx="4" fill="rgba(255,255,255,0.1)"/>
            <circle cx="210" cy="80" r="14" fill="rgba(255,255,255,0.08)"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Right panel (login form) -->
    <div class="login-right">
      <div class="login-card">
        <div class="login-card-header">
          <h2>Đăng nhập</h2>
          <p>Chào mừng! Vui lòng đăng nhập để tiếp tục.</p>
        </div>

        <!-- Alert -->
        <div v-if="errorMsg" class="alert alert-error" role="alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ errorMsg }}
        </div>

        <form @submit.prevent="handleLogin" novalidate>
          <div class="form-group">
            <label class="form-label" for="login-username">Tên đăng nhập</label>
            <input
              id="login-username"
              v-model="username"
              type="text"
              class="form-control"
              placeholder="Nhập tên đăng nhập"
              autocomplete="username"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="login-password">Mật khẩu</label>
            <input
              id="login-password"
              v-model="password"
              type="password"
              class="form-control"
              placeholder="Nhập mật khẩu"
              autocomplete="current-password"
              :disabled="loading"
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary btn-login"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

/* ---- Left panel ---- */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  display: none; /* hidden on mobile */
}

@media (min-width: 900px) {
  .login-left {
    display: flex;
  }
}

.login-left-content {
  max-width: 360px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.brand-icon-lg {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
  margin-bottom: 0.5rem;
}

.login-left-content h1 {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.login-left-content p {
  font-size: 1rem;
  opacity: 0.8;
  line-height: 1.7;
}

.login-illustration {
  margin-top: 1rem;
  opacity: 0.85;
}

/* ---- Right panel ---- */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  padding: 2.5rem;
}

.login-card-header {
  margin-bottom: 2rem;
}

.login-card-header h2 {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
  margin-bottom: 0.3rem;
}

.login-card-header p {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.btn-login {
  width: 100%;
  height: 46px;
  font-size: 0.95rem;
  justify-content: center;
  margin-top: 0.5rem;
}
</style>
