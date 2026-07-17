<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import StudentTable from '@/components/StudentTable.vue'
import StudentModal from '@/components/StudentModal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { useAuth } from '@/stores/auth.js'
import { getAll, create, update, remove } from '@/api/students.js'

const { state, isAdmin, fetchUser } = useAuth()

// ---- State ----
const students = ref([])
const tableLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

// Modal: thêm/sửa
const showModal = ref(false)
const editingStudent = ref(null) // null = thêm mới
const modalLoading = ref(false)

// Confirm dialog: xóa
const showConfirm = ref(false)
const deletingStudent = ref(null)
const deleteLoading = ref(false)

// ---- Fetch ----
async function loadStudents() {
  tableLoading.value = true
  errorMsg.value = ''
  try {
    const res = await getAll()
    students.value = res.data?.data ?? []
  } catch {
    errorMsg.value = 'Không thể tải danh sách sinh viên. Vui lòng thử lại.'
  } finally {
    tableLoading.value = false
  }
}

onMounted(async () => {
  if (!state.user) await fetchUser()
  await loadStudents()
})

// ---- Notifications ----
let toastTimer = null
function showSuccess(msg) {
  successMsg.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (successMsg.value = ''), 3500)
}

// ---- Modal: Thêm / Sửa ----
function openAddModal() {
  editingStudent.value = null
  showModal.value = true
}

function openEditModal(student) {
  editingStudent.value = { ...student }
  showModal.value = true
}

function closeModal() {
  if (modalLoading.value) return
  showModal.value = false
  editingStudent.value = null
}

async function handleSave(formData) {
  modalLoading.value = true
  errorMsg.value = ''
  try {
    if (editingStudent.value) {
      await update(editingStudent.value.id, formData)
      showSuccess(`Đã cập nhật sinh viên "${formData.name}" thành công.`)
    } else {
      await create(formData)
      showSuccess(`Đã thêm sinh viên "${formData.name}" thành công.`)
    }
    showModal.value = false
    editingStudent.value = null
    await loadStudents()
  } catch (err) {
    const status = err.response?.status
    if (status === 403) {
      errorMsg.value = 'Bạn không có quyền thực hiện thao tác này.'
    } else {
      errorMsg.value = err.response?.data?.message || 'Lưu thông tin thất bại. Vui lòng thử lại.'
    }
  } finally {
    modalLoading.value = false
  }
}

// ---- Confirm: Xóa ----
function openDeleteConfirm(student) {
  deletingStudent.value = student
  showConfirm.value = true
}

function cancelDelete() {
  if (deleteLoading.value) return
  showConfirm.value = false
  deletingStudent.value = null
}

async function handleDelete() {
  if (!deletingStudent.value) return
  deleteLoading.value = true
  errorMsg.value = ''
  try {
    await remove(deletingStudent.value.id)
    showSuccess(`Đã xóa sinh viên "${deletingStudent.value.name}" thành công.`)
    showConfirm.value = false
    deletingStudent.value = null
    await loadStudents()
  } catch (err) {
    const status = err.response?.status
    if (status === 403) {
      errorMsg.value = 'Bạn không có quyền thực hiện thao tác này.'
    } else {
      errorMsg.value = err.response?.data?.message || 'Xóa sinh viên thất bại.'
    }
    showConfirm.value = false
  } finally {
    deleteLoading.value = false
  }
}
</script>

<template>
  <div class="home-page">
    <AppHeader />

    <main class="home-main">
      <div class="home-container">
        <!-- Page Title -->
        <div class="page-header">
          <div class="page-title-area">
            <h2>Danh sách sinh viên</h2>
            <p class="page-subtitle">
              {{ students.length }} sinh viên trong hệ thống
            </p>
          </div>

          <button
            v-if="isAdmin"
            class="btn btn-primary"
            @click="openAddModal"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Thêm sinh viên
          </button>
        </div>

        <!-- Alerts -->
        <Transition name="fade">
          <div v-if="errorMsg" class="alert alert-error" role="alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ errorMsg }}
          </div>
        </Transition>

        <Transition name="fade">
          <div v-if="successMsg" class="alert alert-success" role="status">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            {{ successMsg }}
          </div>
        </Transition>

        <!-- Table -->
        <StudentTable
          :students="students"
          :is-admin="isAdmin"
          :loading="tableLoading"
          @edit="openEditModal"
          @delete="openDeleteConfirm"
        />
      </div>
    </main>

    <!-- Modal thêm/sửa -->
    <StudentModal
      :visible="showModal"
      :student="editingStudent"
      :loading="modalLoading"
      @save="handleSave"
      @close="closeModal"
    />

    <!-- Confirm dialog xóa -->
    <ConfirmDialog
      :visible="showConfirm"
      :student-name="deletingStudent?.name ?? ''"
      :loading="deleteLoading"
      @confirm="handleDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  flex-direction: column;
}

.home-main {
  flex: 1;
  padding: 2rem 1.5rem;
}

.home-container {
  max-width: 1280px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.page-title-area h2 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--color-text-primary);
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 0.2rem;
}

/* Alert fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
