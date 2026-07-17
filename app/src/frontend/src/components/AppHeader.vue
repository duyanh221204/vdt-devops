<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth.js'

const router = useRouter()
const { state, isAdmin, logout } = useAuth()

function handleLogout() {
  logout()
  router.push({ name: 'Login' })
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Logo + Title -->
      <div class="header-brand">
        <div class="brand-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <span class="brand-name">Student Management</span>
      </div>

      <!-- User info + Logout -->
      <div class="header-actions">
        <div class="user-info" v-if="state.user">
          <div class="user-avatar">
            {{ state.user.username?.charAt(0)?.toUpperCase() }}
          </div>
          <div class="user-details">
            <span class="user-name">{{ state.user.username }}</span>
            <span :class="['badge', isAdmin ? 'badge-admin' : 'badge-user']">
              {{ isAdmin ? 'Admin' : 'User' }}
            </span>
          </div>
        </div>

        <button class="btn btn-ghost btn-logout" @click="handleLogout" title="Đăng xuất">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span>Đăng xuất</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.brand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
}

.brand-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary), #818cf8);
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-details {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1;
  white-space: nowrap;
}

.btn-logout {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.btn-logout:hover {
  color: var(--color-danger);
  background: var(--color-danger-light);
  border-color: transparent;
}
</style>
