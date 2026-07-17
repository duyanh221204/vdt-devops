import axios from './axios/index.js'

/**
 * Lấy danh sách tất cả sinh viên
 * @returns {Promise<{ status, message, data: Array<{id, name, year_of_birth}> }>}
 */
export function getAll() {
  return axios.get('/students')
}

/**
 * Lấy sinh viên theo ID
 * @param {number} id
 * @returns {Promise<{ status, message, data: {id, name, year_of_birth} }>}
 */
export function getById(id) {
  return axios.get(`/students/${id}`)
}

/**
 * Tạo sinh viên mới (chỉ admin)
 * @param {{ name: string, year_of_birth: number }} data
 * @returns {Promise<{ status, message, data: {id, name, year_of_birth} }>}
 */
export function create(data) {
  return axios.post('/students', data)
}

/**
 * Cập nhật sinh viên (chỉ admin)
 * @param {number} id
 * @param {{ name: string, year_of_birth: number }} data
 * @returns {Promise<{ status, message, data: {id, name, year_of_birth} }>}
 */
export function update(id, data) {
  return axios.put(`/students/${id}`, data)
}

/**
 * Xóa sinh viên (chỉ admin)
 * @param {number} id
 * @returns {Promise<{ status, message }>}
 */
export function remove(id) {
  return axios.delete(`/students/${id}`)
}
