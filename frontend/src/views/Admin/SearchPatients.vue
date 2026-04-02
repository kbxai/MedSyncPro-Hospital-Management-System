<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold"><i class="bi bi-person-search me-2"></i>Search Patients</h3>
        <p class="text-muted small">Find patients by name or username</p>
      </div>
      <router-link to="/admin" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
      </router-link>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input v-model="searchQuery" @keyup.enter="searchPatients" type="text" class="form-control border-start-0"
            placeholder="Search by patient name or username...">
          <button @click="searchPatients" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Search
          </button>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <span class="fw-bold">Search Results</span>
        <span class="badge bg-primary">{{ patients.length }} found</span>
      </div>
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Username</th>
              <th>Age</th>
              <th>Gender</th>
              <th class="text-center" style="width: 120px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="patient in patients" :key="patient.id">
              <td><span class="badge bg-secondary">{{ patient.id }}</span></td>
              <td class="fw-semibold">{{ patient.name }}</td>
              <td><code>{{ patient.username }}</code></td>
              <td>{{ patient.age }}</td>
              <td>
                <span
                  :class="['badge', patient.gender === 'Male' ? 'bg-info' : patient.gender === 'Female' ? 'bg-danger' : 'bg-secondary']">
                  {{ patient.gender }}
                </span>
              </td>
              <td><button class="btn btn-sm btn-outline-danger" @click="blockPatient(patient.id)">
                  <i class="bi bi-lock me-1">Block</i>
                </button></td>
            </tr>
            <tr v-if="patients.length === 0 && searched">
              <td colspan="5" class="text-center py-5 text-muted">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                No patients found matching "{{ lastQuery }}"
              </td>
            </tr>
            <tr v-if="!searched">
              <td colspan="5" class="text-center py-5 text-muted">
                <i class="bi bi-person-search fs-1 d-block mb-2"></i>
                Enter a search term to find patients
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { notify } from '../../ui/notify';

const searchQuery = ref('');
const patients = ref([]);
const loading = ref(false);
const searched = ref(false);
const lastQuery = ref('');

const searchPatients = async () => {
  if (!searchQuery.value.trim()) {
    notify.warn('Please enter a search term');
    return;
  }

  loading.value = true;
  searched.value = true;
  lastQuery.value = searchQuery.value;

  try {
    const res = await axios.post('/api/admin/search-patients', {
      query: searchQuery.value.trim()
    });
    patients.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Search failed');
    patients.value = [];
  } finally {
    loading.value = false;
  }
};


const blockPatient = async (id) => {
  if (confirm("Are you sure you want to block this patient?")) {
    try {
      await axios.delete(`/api/admin/delete-patient/${id}`);
      notify.success("Patient blocked successfully!");
      searchPatients();
    } catch (err) {
      notify.error(err.response?.data?.msg || "Error blocking patient.");
    }
  }
};
</script>
