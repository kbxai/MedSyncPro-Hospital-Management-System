<template>
  <div class="mt-4 row justify-content-center">
    <div class="col-md-6">
      <div class="card shadow border-0">
        <div class="card-body p-4">
          <h3 class="fw-bold text-success mb-4 text-center">
            <i class="bi bi-clipboard2-pulse"></i> Treatment Record
          </h3>
          <form @submit.prevent="submitTreatment">
            <div class="mb-3">
              <label class="form-label fw-bold small">Diagnosis</label>
              <input type="text" class="form-control" v-model="formData.diagnosis" required placeholder="e.g. Viral Fever">
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold small">Prescription</label>
              <textarea class="form-control" v-model="formData.prescription" rows="3" required placeholder="e.g. Paracetamol 500mg..."></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold small">Doctor's Notes</label>
              <textarea class="form-control" v-model="formData.notes" rows="2" placeholder="Rest for 2 days..."></textarea>
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-success w-100 fw-bold">
                <i class="bi bi-check-circle"></i> Complete Appointment
              </button>
              <button type="button" class="btn btn-secondary" @click="router.push('/doctor')">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';


const router = useRouter();
const formData = reactive({
  diagnosis: '',
  prescription: '',
  notes: ''
});

const submitTreatment = async () => {
  const apptId = sessionStorage.getItem('selectedApptId');
  if (!apptId) {
    notify.error("No appointment selected!");
    return;
  }

  try {
    const res = await axios.post(`/api/doctor/add_treatment/${apptId}`, formData);
    notify.success(res.data.msg);
    sessionStorage.removeItem('selectedApptId');
    router.push('/doctor');
  } catch (err) {
    notify.error(err.response?.data?.msg || "Server connection failed.");
  }
};
</script>