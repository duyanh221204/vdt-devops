import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  // Bắt tất cả các route không tồn tại -> về trang chủ
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation Guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    // Chưa đăng nhập -> vào Login
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && token) {
    // Đã đăng nhập rồi mà vào Login -> về Home
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
