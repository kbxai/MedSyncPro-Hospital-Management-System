<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark"><i class="bi bi-calendar-check"></i> My Appointments</h2>
      <router-link to="/doctor/update-availability" class="btn btn-outline-primary btn-sm shadow-sm">
        <i class="bi bi-clock"></i> Update Availability
      </router-link>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-primary">
            <tr>
              <th>Appt ID</th>
              <th>Patient name</th>
              <th>Date</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id">
              <td>{{ appt.id }}</td>
              <td> <button style="color: black;padding: 8px;margin: 5px;" class="btn btn-sm shadow-sm badge card"
                  @click="Viewhistory(appt.patient_id)">
                  <i class="bi bi-clock-history me-1 text-primary"></i>
                  {{ appt.patient_name }}
                </button></td>
              <td>{{ appt.appointment_date }} | {{ appt.appointment_time }} </td>
              <td><span class="badge bg-warning text-dark">{{ appt.status }}</span></td>
              <td>
                <div v-if="appt.status === 'pending'" class="d-flex gap-1">
                  <button class="btn btn-sm btn-success shadow-sm" @click="openTreatmentForm(appt.id)">
                    <i class="bi bi-capsule"></i> Treat
                  </button>
                  <button class="btn btn-sm btn-danger shadow-sm" @click="cancelAppointment(appt.id)">
                    <i class="bi bi-x-circle"></i> Cancel
                  </button>
                </div>
                <span v-else class="text-muted small">{{ appt.status }}</span>
              </td>
            </tr>
            <tr v-if="appointments.length === 0">
              <td colspan="5" class="text-center py-4 text-muted">No appointments found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="patients.length > 0" class="card shadow-sm border-0">
      <div class="card-header bg-white fw-bold">My Patients</div>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Total Visits</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pat in patients" :key="pat.id">
              <td>{{ pat.name }}</td>
              <td>{{ pat.visits }}</td>
              <td>
                <button class="btn btn-sm btn-outline-primary" @click="Viewhistory(pat.id)">
                  <i class="bi bi-clock-history"></i> View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';

const appointments = ref([]);
const patients = ref([]);
const router = useRouter();

const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/doctor/get_my_appointments/');
    appointments.value = res.data;

    const patMap = {};
    for (const a of res.data) {
      if (!patMap[a.patient_id]) {
        patMap[a.patient_id] = { id: a.patient_id, name: a.patient_name, visits: 0 };
      }
      patMap[a.patient_id].visits++;
    }
    patients.value = Object.values(patMap);
  } catch (err) {
    notify.error(err.response?.data?.msg || "Failed to fetch appointments");
  }
};

const Viewhistory = async (pat_id) => {
  router.push({ path: '/doctor/patient-history', query: { pat_id } });
};

const openTreatmentForm = (apptId) => {
  sessionStorage.setItem('selectedApptId', apptId);
  router.push('/doctor/add-treatment');
};

const cancelAppointment = async (apptId) => {
  if (!confirm('Cancel this appointment?')) return;
  try {
    await axios.put(`/api/doctor/cancel-appointment/${apptId}`);
    notify.success('Appointment cancelled');
    await fetchAppointments();
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Cancel failed');
  }
};

onMounted(fetchAppointments);
</script>