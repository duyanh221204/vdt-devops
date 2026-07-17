import axios from './axios/index.js'

/**
 * Lấy thông tin user hiện tại (yêu cầu token)
 * @returns {Promise<{ id: number, username: string, role: string }>}
 */
export function getMe() {
  return axios.get('/users/me')
}
