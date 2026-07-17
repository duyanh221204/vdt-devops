<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  student: {
    type: Object,
    default: null, // null = thêm mới, object = sửa
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['save', 'close'])

const isEditing = computed(() => !!props.student)
const title = computed(() => (isEditing.value ? 'Sửa sinh viên' : 'Thêm sinh viên'))

// Form state
const form = ref({ name: '', year_of_birth: '' })
const errors = ref({ name: '', year_of_birth: '' })

// Sync form với props.student khi mở modal
watch(
  () => props.visible,
  (val) => {
    if (val) {
      if (props.student) {
        form.value = { name: props.student.name, year_of_birth: props.student.year_of_birth }
      } else {
        form.value = { name: '', year_of_birth: '' }
      }
      errors.value = { name: '', year_of_birth: '' }
    }
  }
)

function validate() {
  let valid = true
  errors.value = { name: '', year_of_birth: '' }

  if (!form.value.name || !form.value.name.trim()) {
    errors.value.name = 'Họ tên không được để trống.'
    valid = false
  }

  const year = Number(form.value.year_of_birth)
  if (!form.value.year_of_birth && form.value.year_of_birth !== 0) {
    errors.value.year_of_birth = 'Năm sinh là bắt buộc.'
    valid = false
  } else if (!Number.isInteger(year) || year < 2000 || year > 2010) {
    errors.value.year_of_birth = 'Năm sinh phải trong khoảng 2000 – 2010.'
    valid = false
  }

  return valid
}

function handleSubmit() {
  if (!validate()) return
  emit('save', {
    name: form.value.name.trim(),
    year_of_birth: Number(form.value.year_of_birth),
  })
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-box" role="dialog" :aria-label="title">
          <!-- Header -->
          <div class="modal-header">
            <h3>{{ title }}</h3>
            <button class="modal-close-btn" @click="emit('close')" :disabled="loading">✕</button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- Họ tên -->
            <div class="form-group">
              <label class="form-label" for="field-name">
                Họ và tên <span class="required">*</span>
              </label>
              <input
                id="field-name"
                v-model="form.name"
                type="text"
                :class="['form-control', errors.name ? 'is-error' : '']"
                placeholder="Nhập họ tên sinh viên"
                :disabled="loading"
                @keyup.enter="handleSubmit"
              />
              <p v-if="errors.name" class="form-error">{{ errors.name }}</p>
            </div>

            <!-- Năm sinh -->
            <div class="form-group" style="margin-bottom: 0">
              <label class="form-label" for="field-year">
                Năm sinh <span class="required">*</span>
              </label>
              <input
                id="field-year"
                v-model="form.year_of_birth"
                type="number"
                :class="['form-control', errors.year_of_birth ? 'is-error' : '']"
                placeholder="2000 – 2010"
                min="2000"
                max="2010"
                :disabled="loading"
                @keyup.enter="handleSubmit"
              />
              <p v-if="errors.year_of_birth" class="form-error">{{ errors.year_of_birth }}</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="emit('close')" :disabled="loading">
              Hủy
            </button>
            <button class="btn btn-primary" @click="handleSubmit" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              {{ isEditing ? 'Cập nhật' : 'Thêm mới' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.required {
  color: var(--color-danger);
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
