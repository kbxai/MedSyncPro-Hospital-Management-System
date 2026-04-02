<template>
  <div class="mt-4 row justify-content-center">
    <div class="col-md-6">
      <div class="card shadow-lg border-0 p-4" v-if="doctor">
        <h4 class="fw-bold text-center mb-4 text-primary">
          <i class="bi bi-calendar-plus me-2"></i>Book with Dr. {{ doctor.name }}
          <div class="small text-muted mt-1">
            <i class="bi bi-hospital me-1"></i> {{ doctor.department }} |
            <i class="bi bi-clock me-1"></i> {{ doctor.availability?.replace('|', ' | ') }}
          </div>
        </h4>

        <div class="mb-4">
          <label class="form-label small fw-bold">1. Select Visit Date</label>
          <input type="date" class="form-control rounded-3" v-model="formData.date" @change="fetchSlots" :min="minDate">
        </div>

        <div v-if="formData.date" class="mb-4">
          <label class="form-label small fw-bold">2. Select a Time Slot</label>
          <div v-if="loading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary"></div>
          </div>

          <div v-else class="slot-grid mt-2">
            <button v-for="slot in availableSlots" :key="slot" type="button"
              :class="['btn btn-sm slot-btn', formData.time === slot ? 'btn-primary active' : 'btn-outline-primary']"
              @click="formData.time = slot">
              {{ slot }}
            </button>
          </div>
          <p v-if="!loading && availableSlots.length === 0" class="text-danger small mt-2">
            No slots available for this date. Please try another day.
          </p>
        </div>

        <button :disabled="loading || !formData.time" @click="confirmBooking" class="btn btn-primary w-100 fw-bold py-2 shadow-sm">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Confirm Appointment
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';


const router = useRouter();
const doctor = ref(null);
const availableSlots = ref([]);
const loading = ref(false);
const minDate = new Date().toISOString().split('T')[0];

const formData = reactive({ date: '', time: '' });

onMounted(() => {
  const data = sessionStorage.getItem('selectedDoctor');
  if (data) doctor.value = JSON.parse(data);
  else router.push('/patient');
});


const fetchSlots = async () => {
  if (!formData.date || !doctor.value?.id) return;

  loading.value = true;
  formData.time = '';
  availableSlots.value = [];

  try {
    const res = await axios.post('/api/patient/get-available-slots', {
      doct_id: doctor.value.id,
      date: formData.date
    });
    availableSlots.value = Array.isArray(res.data) ? res.data : [];
  }
  catch (err) {
    const msg = err.response?.data?.msg || `Error loading slots (HTTP ${err.response?.status || '??'})`;

    notify.error(msg);
  } finally {
    loading.value = false;
  }
};

const confirmBooking = async () => {
  if (!formData.date || !formData.time) return;

  if (!confirm(`Book appointment with Dr. ${doctor.value.name} on ${formData.date} at ${formData.time}?`)) {
    return;
  }

  loading.value = true;
  try {
    await axios.post('/api/patient/book-appointment/', {
      doct_id: doctor.value.id,
      date: formData.date,
      time: formData.time
    });

    notify.success('Appointment booked successfully!');
    router.push('/patient/appointments');
  } catch (err) {
    const msg = err.response?.data?.msg || 'Booking failed';
    notify.error(msg);
  } finally {
    loading.value = false;
  }
};

</script>

<style scoped>
.slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
}

.slot-btn {
  border-radius: 8px;
  padding: 8px;
  font-weight: 600;
  transition: all 0.2s;
}

.slot-btn.active {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(13, 110, 253, 0.3);
}
</style>