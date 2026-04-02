<template>
  <div class="mt-4">
    <div class="row mb-4 align-items-center">
      <div class="col-md-8">
        <h2 class="fw-bold text-dark"><i class="bi bi-search"></i> Find a Doctor</h2>
      </div>
      <div class="col-md-4 text-end">
        <router-link to="/patient/update-profile" class="btn btn-outline-primary btn-sm shadow-sm me-2">
          <i class="bi bi-person-gear"></i> Update Profile
        </router-link>
        <router-link to="/patient/appointments" class="btn btn-secondary btn-sm shadow-sm">
          <i class="bi bi-list-check"></i> My Appointments
        </router-link>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <select class="form-select" v-model="selectedDept" @change="fetchDoctors">
          <option :value="null">All Departments</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
        </select>
      </div>
      <div class="col-md-4">
        <input type="text" class="form-control" placeholder="Search by doctor name..." v-model="searchName"
          @input="filterDoctors">
      </div>
    </div>

    <div class="row g-4">
      <div v-for="doc in filteredDoctors" :key="doc.id" class="col-md-4">
        <div class="card h-100 shadow-sm border-0 doctor-card">
          <div class="card-body">
            <h5 class="card-title fw-bold text-primary">Dr. {{ doc.name }}</h5>
            <p class="mb-1 text-muted small"><i class="bi bi-hospital"></i> {{ doc.department }}</p>
            <p class="mb-3 small text-secondary"><i class="bi bi-clock"></i> {{ doc.availability?.replace('|', ' | ') }}
            </p>
            <button class="btn btn-outline-primary w-100 btn-sm fw-bold" @click="goToBooking(doc)">
              Book Appointment
            </button>
          </div>
        </div>
      </div>
      <div v-if="filteredDoctors.length === 0" class="text-center py-5">
        <p class="text-muted">No doctors found.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';

const doctors = ref([]);
const departments = ref([]);
const selectedDept = ref(null);
const searchName = ref('');
const router = useRouter();

const filteredDoctors = computed(() => {
  if (!searchName.value.trim()) return doctors.value;
  const q = searchName.value.toLowerCase();
  return doctors.value.filter(d => d.name.toLowerCase().includes(q));
});

const fetchDepartments = async () => {
  try {
    const res = await axios.get('/api/admin/get-departments');
    departments.value = res.data;
  } catch (err) { void err; }
};

const fetchDoctors = async () => {
  try {
    const res = await axios.post('/api/patient/search-doctors/', {
      dept_id: selectedDept.value,
    });
    doctors.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || "Failed to load doctors");
  }
};

const goToBooking = (doc) => {
  sessionStorage.setItem('selectedDoctor', JSON.stringify(doc));
  router.push('/patient/book');
};

onMounted(() => {
  fetchDepartments();
  fetchDoctors();
});
</script>