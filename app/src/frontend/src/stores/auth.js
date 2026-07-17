import { reactive, computed } from 'vue'
import { getMe } from '@/api/users.js'

const state = reactive({
  user: null,
  loading: false,
  error: null,
})

const isAdmin = computed(() => state.user?.role === 'admin')

async function fetchUser() {
  state.loading = true
  state.error = null
  try {
    const res = await getMe()
    state.user = res.data
  } catch (err) {
    state.user = null
    state.error = err
  } finally {
    state.loading = false
  }
}

function logout() {
  localStorage.removeItem('access_token')
  state.user = null
}

export function useAuth() {
  return {
    state,
    isAdmin,
    fetchUser,
    logout,
  }
}
