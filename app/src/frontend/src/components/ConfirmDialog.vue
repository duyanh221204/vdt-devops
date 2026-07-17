<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  studentName: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="emit('cancel')">
        <div class="modal-box confirm-box" role="alertdialog" aria-label="Xác nhận xóa">
          <!-- Icon -->
          <div class="confirm-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14H6L5 6"/>
              <path d="M10 11v6M14 11v6"/>
              <path d="M9 6V4h6v2"/>
            </svg>
          </div>

          <!-- Content -->
          <div class="confirm-content">
            <h3>Xác nhận xóa</h3>
            <p>
              Bạn có chắc muốn xóa sinh viên
              <strong>&ldquo;{{ studentName }}&rdquo;</strong>?
              Hành động này không thể hoàn tác.
            </p>
          </div>

          <!-- Buttons -->
          <div class="confirm-actions">
            <button class="btn btn-secondary" @click="emit('cancel')" :disabled="loading">
              Hủy bỏ
            </button>
            <button class="btn btn-danger" @click="emit('confirm')" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              Xóa sinh viên
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-box {
  max-width: 400px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.confirm-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: var(--radius-full);
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.confirm-content h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.35rem;
}

.confirm-content p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  justify-content: center;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition);
}
.modal-enter-active .modal-box,
.modal-leave-active .modal-box {
  transition: transform var(--transition), opacity var(--transition);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-box,
.modal-leave-to .modal-box {
  transform: translateY(12px) scale(0.97);
  opacity: 0;
}
</style>
