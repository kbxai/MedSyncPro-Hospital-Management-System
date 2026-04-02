<template>
  <div class="mt-4">
    <header class="mb-5">
      <h2 class="fw-bold">Dashboard Summary</h2>
      <p class="text-muted">Welcome back, Admin. Here's what's happening today.</p>
    </header>

    <div class="row g-3 mb-5">
      <div class="col-md-3" v-for="stat in stats" :key="stat.label">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center">
            <div
              :class="['icon-box rounded-circle d-flex align-items-center justify-content-center me-3', stat.colorClass]"
              style="width: 50px; height: 50px;">
              <i :class="['bi fs-4 text-white', stat.icon]"></i>
            </div>
            <div>
              <h3 class="fw-bold mb-0">{{ stat.value }}</h3>
              <small class="text-muted">{{ stat.label }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-4" v-for="item in menuItems" :key="item.title">
        <div class="card shadow-sm h-100 p-3">
          <div class="card-body">
            <div
              :class="['icon-box mb-3 rounded-circle d-flex align-items-center justify-content-center', item.colorClass]"
              style="width: 50px; height: 50px;">
              <i :class="['bi fs-4 text-white', item.icon]"></i>
            </div>
            <h5 class="fw-bold">{{ item.title }}</h5>
            <p class="text-muted small">{{ item.desc }}</p>
            <router-link :to="item.link" class="btn btn-outline-primary btn-sm w-100 mt-3">Access Portal</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { notify } from '../../ui/notify';

const stats = ref([
  { label: 'Total Doctors', value: 0, icon: 'bi-person-badge', colorClass: 'bg-primary' },
  { label: 'Total Patients', value: 0, icon: 'bi-people', colorClass: 'bg-success' },
  { label: 'Appointments', value: 0, icon: 'bi-calendar-check', colorClass: 'bg-info' },
  { label: 'Pending', value: 0, icon: 'bi-clock-history', colorClass: 'bg-warning' }
]);

const menuItems = [
  { title: 'Departments', icon: 'bi-hospital', desc: 'Manage hospital units and specialties.', link: '/admin/departments', colorClass: 'bg-primary' },
  { title: 'Doctor Directory', icon: 'bi-person-badge', desc: 'View and manage medical staff.', link: '/admin/view-doctors', colorClass: 'bg-success' },
  { title: 'Search Doctors', icon: 'bi-search', desc: 'Find doctors by name or department.', link: '/admin/search-doctors', colorClass: 'bg-info' },
  { title: 'Search Patients', icon: 'bi-search', desc: 'Find patients by name or ID.', link: '/admin/search-patients', colorClass: 'bg-secondary' },
  { title: 'All Appointments', icon: 'bi-calendar-week', desc: 'View and manage all appointments.', link: '/admin/appointments', colorClass: 'bg-warning' },
  { title: 'Add Doctor', icon: 'bi-person-plus', desc: 'Register a new doctor to system.', link: '/admin/add-doctor', colorClass: 'bg-dark' }
];

const fetchStats = async () => {
  try {
    const res = await axios.get('/api/admin/get-dashboard-stats');
    stats.value[0].value = res.data.total_doctors;
    stats.value[1].value = res.data.total_patients;
    stats.value[2].value = res.data.total_appointments;
    stats.value[3].value = res.data.pending_appointments;
  } catch (err) {
    notify.error('Failed to fetch stats');
  }
};

onMounted(fetchStats);
</script>