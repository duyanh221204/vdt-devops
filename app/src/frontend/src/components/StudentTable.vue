<script setup>
defineProps({
  students: {
    type: Array,
    default: () => [],
  },
  isAdmin: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['edit', 'delete'])
</script>

<template>
  <div class="table-wrapper">
    <!-- Loading state -->
    <div v-if="loading" class="empty-state">
      <span class="spinner spinner-dark"></span>
      <p>Đang tải danh sách sinh viên...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="!students.length" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="7" r="4"/>
        <path d="M5.5 21a8.38 8.38 0 0 1 13 0"/>
      </svg>
      <p>Chưa có sinh viên nào.</p>
    </div>

    <!-- Data table -->
    <table v-else class="table">
      <thead>
        <tr>
          <th style="width: 60px">#</th>
          <th>Họ và tên</th>
          <th style="width: 140px">Năm sinh</th>
          <th v-if="isAdmin" style="width: 160px; text-align: center">Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(student, index) in students" :key="student.id">
          <td class="index-cell">{{ index + 1 }}</td>
          <td>
            <div class="student-name-cell">
              <div class="student-avatar">{{ student.name?.charAt(0)?.toUpperCase() }}</div>
              <span>{{ student.name }}</span>
            </div>
          </td>
          <td>
            <span class="year-badge">{{ student.year_of_birth }}</span>
          </td>
          <td v-if="isAdmin">
            <div class="actions-cell">
              <button
                class="btn btn-secondary btn-sm"
                @click="emit('edit', student)"
                title="Sửa sinh viên"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Sửa
              </button>
              <button
                class="btn btn-danger btn-sm"
                @click="emit('delete', student)"
                title="Xóa sinh viên"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14H6L5 6"/>
                  <path d="M10 11v6M14 11v6"/>
                  <path d="M9 6V4h6v2"/>
                </svg>
                Xóa
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.index-cell {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.student-name-cell {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.student-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #a5b4fc, #6366f1);
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.year-badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  background: #f1f5f9;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}
</style>
