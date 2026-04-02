<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold"><i class="bi bi-search me-2"></i>Search Doctors</h3>
        <p class="text-muted small">Find doctors by name or department</p>
      </div>
      <router-link to="/admin/view-doctors" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back to All Doctors
      </router-link>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input 
            v-model="searchQuery" 
            @keyup.enter="searchDoctors"
            type="text" 
            class="form-control border-start-0" 
            placeholder="Search by doctor name or department..."
          >
          <button @click="searchDoctors" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Search
          </button>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
        <span class="fw-bold">Search Results</span>
        <span class="badge bg-primary">{{ doctors.length }} found</span>
      </div>
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Department</th>
              <th>Availability</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in doctors" :key="doc.id">
              <td><span class="badge bg-secondary">{{ doc.id }}</span></td>
              <td class="fw-semibold">Dr. {{ doc.name }}</td>
              <td><span class="badge bg-info text-dark">{{ doc.department }}</span></td>
              <td><code class="small">{{ doc.availability }}</code></td>
              <td>
                <button @click="blockDoctor(doc.id)" class="btn btn-sm btn-outline-danger">
                  <i class="bi bi-slash-circle me-1"></i>Block
                </button>
              </td>
            </tr>
            <tr v-if="doctors.length === 0 && searched">
              <td colspan="5" class="text-center py-5 text-muted">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                No doctors found matching "{{ lastQuery }}"
              </td>
            </tr>
            <tr v-if="!searched">
              <td colspan="5" class="text-center py-5 text-muted">
                <i class="bi bi-search fs-1 d-block mb-2"></i>
                Enter a search term to find doctors
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
const doctors = ref([]);
const loading = ref(false);
const searched = ref(false);
const lastQuery = ref('');

const searchDoctors = async () => {
  if (!searchQuery.value.trim()) {
    notify.warn('Please enter a search term');
    return;
  }

  loading.value = true;
  searched.value = true;
  lastQuery.value = searchQuery.value;

  try {
    const res = await axios.post('/api/admin/search-doctors', {
      query: searchQuery.value.trim()
    });
    doctors.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Search failed');
    doctors.value = [];
  } finally {
    loading.value = false;
  }
};

const blockDoctor = async (id) => {
  if (!confirm('Block this doctor? All pending appointments will be cancelled.')) return;

  try {
    await axios.delete(`/api/admin/delete-doctor/${id}`);
    notify.success('Doctor blocked successfully');
    doctors.value = doctors.value.filter(d => d.id !== id);
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Failed to block doctor');
  }
};
</script>
