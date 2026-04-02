<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold text-primary mb-0">
        <i class="bi bi-people-fill me-2"></i>Manage Doctors
      </h3>
      <div>
        <router-link to="/admin/add-doctor" class="btn btn-success me-2 shadow-sm">
          <i class="bi bi-person-plus-fill me-1"></i> Add New
        </router-link>
        <router-link to="/admin" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i> Back
        </router-link>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-4" style="width: 80px;">ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Availability</th>
                <th class="text-center" style="width: 120px;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in doctors" :key="doc.id">
                <td class="ps-4">
                  <span class="text-muted">#{{ doc.id }}</span>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div
                      class="avatar-sm bg-primary bg-opacity-10 rounded-circle me-2 d-flex align-items-center justify-content-center">
                      <i class="bi bi-person text-primary"></i>
                    </div>
                    <span class="fw-semibold">Dr. {{ doc.name }}</span>
                  </div>
                </td>
                <td>
                  <span class="badge bg-opacity-15 text-info px-2 py-1">
                    {{ doc.department }}
                  </span>
                </td>
                <td>
                  <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>{{ doc.availability }}
                  </small>
                </td>
                <td class="text-center">
                  <button class="btn btn-sm btn-outline-danger" @click="blockDoctor(doc.id)">
                    <i class="bi bi-x-circle me-1">Block</i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="updateDoctor(doc.id)">
                    <i class="bi bi-pencil me-1">Update</i>
                  </button>
                </td>
              </tr>
              <tr v-if="doctors.length === 0">
                <td colspan="5" class="text-center py-5 text-muted">
                  <i class="bi bi-inbox fs-2 d-block mb-2 opacity-50"></i>
                  <p class="mb-0">No doctors found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { notify } from '../../ui/notify';
import { useRouter } from 'vue-router';

const doctors = ref([]);
const router = useRouter();

const fetchDoctors = async () => {
  try {
    const res = await axios.get('/api/admin/get_all_doctors');
    doctors.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Failed to load doctors')
  }
};

const blockDoctor = async (id) => {
  if (confirm("Are you sure you want to block this doctor?")) {
    try {
      await axios.delete(`/api/admin/delete-doctor/${id}`);
      notify.success("Doctor blocked successfully!");
      fetchDoctors();
    } catch (err) {
      notify.error(err.response?.data?.msg || "Error blocking doctor.");
    }
  }
};


const updateDoctor = (id) => {
  try {
    router.push({
      path: '/admin/update-doctor',
      query: { id: id }
    });
  } catch (err) {
    notify.error("Error updating doctor.", err.error);
  }


}
onMounted(fetchDoctors);
</script>

<style scoped>
.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 0.9rem;
}

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
  vertical-align: middle;
  border-bottom: 1px solid #f1f5f9;
}

.table tbody tr:hover {
  background-color: #f8fafc;
}

.badge {
  font-weight: 500;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: white;
}
</style>