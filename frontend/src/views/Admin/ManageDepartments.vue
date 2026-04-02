<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { notify } from '../../ui/notify';

const departments = ref([]);
const name = ref('');
const description = ref('');
const isLoading = ref(false);

const fetchDepartments = async () => {
  try {
    const res = await axios.get('/api/admin/get-departments');
    departments.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || "Failed to load departments");
  }
};

const addDepartment = async () => {
  if (isLoading.value) return;
  isLoading.value = true;

  try {
    const res = await axios.post('/api/admin/add-department', {
      name: name.value,
      description: description.value
    });
    notify.success(res.data.msg || "Department added!");
    name.value = '';
    description.value = '';
    fetchDepartments();
  } catch (err) {
    notify.error(err.response?.data?.msg || "Failed to add department");
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchDepartments);
</script>

<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold text-primary mb-0">
        <i class="bi bi-hospital me-2"></i>Manage Departments
      </h3>
      <router-link to="/admin" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back
      </router-link>
    </div>

    <div class="row g-4">
      <div class="col-md-5">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h5 class="fw-bold mb-3">
              <i class="bi bi-plus-circle me-2 text-success"></i>Add New Department
            </h5>
            <form @submit.prevent="addDepartment">
              <div class="mb-3">
                <label class="form-label small fw-bold">Department Name</label>
                <input v-model="name" type="text" class="form-control" placeholder="e.g. Cardiology" required>
              </div>
              <div class="mb-4">
                <label class="form-label small fw-bold">Description (Optional)</label>
                <textarea v-model="description" class="form-control" rows="3"
                  placeholder="e.g. Heart and cardiovascular diseases"></textarea>
              </div>
              <button type="submit" class="btn btn-success w-100 fw-bold" :disabled="isLoading">
                <span v-if="isLoading">
                  <span class="spinner-border spinner-border-sm me-2"></span>Adding...
                </span>
                <span v-else>
                  <i class="bi bi-plus-circle me-1"></i>Add Department
                </span>
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-7">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white py-3 border-0">
            <h5 class="fw-bold mb-0">
              <i class="bi bi-list-ul me-2 text-primary"></i>Existing Departments
              <span class="badge bg-primary ms-2">{{ departments.length }}</span>
            </h5>
          </div>
          <div class="card-body p-0">
            <div v-if="departments.length" class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4">ID</th>
                    <th>Department Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dept in departments" :key="dept.id">
                    <td class="ps-4">
                      <span class="badge bg-light text-dark border">#{{ dept.id }}</span>
                    </td>
                    <td>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-hospital text-primary me-2 fs-5"></i>
                        <span class="fw-semibold">{{ dept.name }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-else class="p-5 text-center text-muted">
              <i class="bi bi-inbox fs-1 d-block mb-3 opacity-50"></i>
              <p class="mb-1 fw-semibold">No departments yet</p>
              <small>Add your first department using the form</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  border-bottom: 2px solid #e2e8f0;
  padding: 0.875rem 0.75rem;
}

.table td {
  padding: 0.875rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.table tbody tr:hover {
  background-color: #f8fafc;
}
</style>