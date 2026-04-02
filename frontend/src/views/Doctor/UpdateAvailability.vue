<template>
  <div class="mt-4 row justify-content-center">
    <div class="col-md-6">
      <div class="card shadow-sm border-0 p-4">
        <h4 class="fw-bold text-primary mb-4 text-center">Update Availability</h4>

        <form @submit.prevent="saveAvailability">
          <div class="mb-3">
            <label class="form-label small fw-bold">Available Days</label>
            <div class="d-flex flex-wrap gap-2">
              <div v-for="day in allDays" :key="day" class="form-check">
                <input class="form-check-input" type="checkbox" :value="day" v-model="selectedDays" :id="day">
                <label class="form-check-label" :for="day">{{ day }}</label>
              </div>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div class="col-6">
              <label class="form-label small fw-bold">Start Time</label>
              <input type="time" class="form-control" v-model="startTime" required>
            </div>
            <div class="col-6">
              <label class="form-label small fw-bold">End Time</label>
              <input type="time" class="form-control" v-model="endTime" required>
            </div>
          </div>

          <div v-if="preview" class="alert alert-info small mb-3">
            <strong>Preview:</strong> {{ preview }}
          </div>

          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary w-100 fw-bold" :disabled="selectedDays.length === 0">
              Save Availability
            </button>
            <button type="button" class="btn btn-secondary" @click="router.push('/doctor')">Back</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';

const router = useRouter();
const allDays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const selectedDays = ref([]);
const startTime = ref('09:00');
const endTime = ref('17:00');

const preview = computed(() => {
  if (selectedDays.value.length === 0) return '';
  return selectedDays.value.join(',') + '|' + startTime.value + '-' + endTime.value;
});

onMounted(async () => {
  try {
    await axios.get('/api/doctor/get_my_appointments/');
  } catch (err) { void err; }
});

const saveAvailability = async () => {
  if (selectedDays.value.length === 0) {
    notify.error('Select at least one day');
    return;
  }
  if (startTime.value >= endTime.value) {
    notify.error('End time must be after start time');
    return;
  }

  const availability = selectedDays.value.join(',') + '|' + startTime.value + '-' + endTime.value;

  try {
    await axios.put('/api/doctor/update-availability', { availability });
    notify.success('Availability updated');
    router.push('/doctor');
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Update failed');
  }
};
</script>
