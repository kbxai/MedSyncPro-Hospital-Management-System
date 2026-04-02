<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold"><i class="bi bi-calendar-check me-2"></i>All Appointments</h3>
        <p class="text-muted small">View and manage all system appointments</p>
      </div>
      <router-link to="/admin" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
      </router-link>
    </div>

    <div class="mb-4">
      <div class="btn-group" role="group">
        <button v-for="filter in filters" :key="filter.value" @click="activeFilter = filter.value"
          :class="['btn', activeFilter === filter.value ? 'btn-primary' : 'btn-outline-primary']">
          {{ filter.label }}
          <span class="badge bg-white text-primary ms-1">{{ getFilterCount(filter.value) }}</span>
        </button>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in filteredAppointments" :key="appt.id">
              <td><span class="badge bg-secondary">{{ appt.id }}</span></td>
              <td class="fw-semibold">{{ appt.patient_name }}</td>
              <td>Dr. {{ appt.doctor_name }}</td>
              <td>{{ formatDate(appt.date) }}</td>
              <td>{{ appt.time }}</td>
              <td>
                <span :class="['badge', getStatusClass(appt.status)]">
                  {{ appt.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredAppointments.length === 0">
              <td colspan="6" class="text-center py-5 text-muted">
                <i class="bi bi-calendar-x fs-1 d-block mb-2"></i>
                No {{ activeFilter === 'all' ? '' : activeFilter }} appointments found
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { notify } from '../../ui/notify';

const appointments = ref([]);
const activeFilter = ref('all');

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
];

const filteredAppointments = computed(() => {
  if (activeFilter.value === 'all') return appointments.value;
  return appointments.value.filter(a => a.status === activeFilter.value);
});

const getFilterCount = (filter) => {
  if (filter === 'all') return appointments.value.length;
  return appointments.value.filter(a => a.status === filter).length;
};

const getStatusClass = (status) => {
  const classes = {
    'pending': 'bg-warning text-dark',
    'completed': 'bg-success',
    'cancelled': 'bg-danger'
  };
  return classes[status] || 'bg-secondary';
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
};

const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/admin/get-all-appointments');
    appointments.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Failed to load appointments');
  }
};

onMounted(fetchAppointments);
</script>
