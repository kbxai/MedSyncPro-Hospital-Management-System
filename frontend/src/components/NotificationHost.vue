<template>
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1080;">
    <div
      v-for="t in notifyState.items"
      :key="t.id"
      class="toast show border-0 shadow-sm mb-2"
      :class="toastBg(t.variant)"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="toast-body d-flex align-items-start gap-2">
        <i :class="toastIcon(t.variant)" class="mt-1"></i>

        <div class="flex-grow-1">
          <div class="fw-semibold small text-body">{{ title(t.variant) }}</div>
          <div class="small text-body-secondary">{{ t.message }}</div>
        </div>
      </div>

      <div class="toast-progress" :style="{ animationDuration: (t.duration || 3000) + 'ms' }"></div>
    </div>
  </div>
</template>

<script setup>
import { notifyState } from '../ui/notify';

const toastBg = (v) => {
  if (v === 'success') return 'bg-success-subtle';
  if (v === 'danger') return 'bg-danger-subtle';
  if (v === 'warning') return 'bg-warning-subtle';
  return 'bg-info-subtle';
};

const toastIcon = (v) => {
  if (v === 'success') return 'bi bi-check-circle-fill text-success';
  if (v === 'danger') return 'bi bi-x-circle-fill text-danger';
  if (v === 'warning') return 'bi bi-exclamation-triangle-fill text-warning';
  return 'bi bi-info-circle-fill text-info';
};

const title = (v) => {
  if (v === 'success') return 'Success';
  if (v === 'danger') return 'Error';
  if (v === 'warning') return 'Warning';
  return 'Info';
};
</script>

<style scoped>
.toast {
  width: 340px;
  border-radius: 12px;
  overflow: hidden;
}

.toast-progress {
  height: 3px;
  background: rgba(13, 110, 253, 0.55);
  animation-name: toastShrink;
  animation-timing-function: linear;
  animation-fill-mode: forwards;
}

.bg-success-subtle .toast-progress { background: rgba(25, 135, 84, 0.55); }
.bg-danger-subtle  .toast-progress { background: rgba(220, 53, 69, 0.55); }
.bg-warning-subtle .toast-progress { background: rgba(255, 193, 7, 0.70); }

@keyframes toastShrink {
  from { width: 100%; }
  to   { width: 0%; }
}
</style>