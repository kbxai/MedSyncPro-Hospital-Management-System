<template>
    <div class="mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h3 class="fw-bold"><i class="bi bi-person-search me-2"></i>Patient history</h3>
            </div>
            <router-link to="/doctor" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-arrow-left me-1"></i> Back to Dashboard
            </router-link>
        </div>
        <div class="card-body p-0 table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Appointment id</th>
                        <th>Diagnosis</th>
                        <th>Prescription</th>
                        <th>Notes</th>
                        <th>Appointment date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="treat in history" :key="treat.treatment_id">
                        <td><span class="badge bg-secondary">{{ treat.appointment_id }}</span></td>
                        <td class="fw-semibold">{{ treat.diagnosis }}</td>
                        <td><code>{{ treat.prescription }}</code></td>
                        <td>{{ treat.notes }}</td>
                        <td>
                            <span class="badge bg-info text-dark"> {{ treat.appointment_date }} | {{ treat.appointment_time }} </span>
                        </td>
                    </tr>
                    <tr v-if="history.length === 0 && !loading">
                        <td colspan="5" class="text-center py-5 text-muted">
                            <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                            No history found for this patient.
                        </td>
                    </tr>

                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { notify } from '../../ui/notify';


const loading = ref(false);
const history = ref([]);
const router = useRouter();
const route = useRoute();

onMounted(async () => {
    try {
        const pat_id = route.query.pat_id;
        if (!pat_id) {
            notify.error('No patient ID provided');
            router.push('/doctor');
            return;
        }
        const res = await axios.get(`/api/doctor/patient-history/${pat_id}`);
        const data = res.data;

        history.value = data;

       
    } catch (err) {
        notify.error(err.response?.data?.msg || 'fetching patient history failed');
        history.value = [];
    } finally {
        loading.value = false;
    }
});

</script>
