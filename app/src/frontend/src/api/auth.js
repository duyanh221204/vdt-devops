import axios from './axios/index.js'

/**
 * Đăng nhập với username và password (x-www-form-urlencoded)
 * @param {string} username
 * @param {string} password
 * @returns {Promise<{ access_token: string }>}
 */
export function login(username, password) {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  return axios.post('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}
