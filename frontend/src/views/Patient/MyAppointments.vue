<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold text-primary"><i class="bi bi-person-lines-fill"></i> My Bookings & Records</h3>
      <div>
        <button @click="triggerExport" class="btn btn-sm btn-success shadow-sm me-2">
          <i class="bi bi-file-earmark-spreadsheet"></i> Export History (CSV)
        </button>
        <router-link to="/patient" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left"></i> Back to Search
        </router-link>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-info">
            <tr>
              <th>Doctor</th>
              <th>Date & Time</th>
              <th>Status</th>
              <th>Treatment / Prescription</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in my_appts" :key="appt.id">
              <td>
                <div class="fw-bold text-dark">Dr. {{ appt.doctor_name }}</div>
              </td>
              <td><small>{{ appt.date }} | {{ appt.time }}</small></td>
              <td>
                <span class="badge rounded-pill"
                  :class="appt.status === 'completed' ? 'bg-success' : appt.status === 'cancelled' ? 'bg-danger' : 'bg-warning text-dark'">
                  {{ appt.status }}
                </span>
              </td>
              <td>
                <div v-if="appt.status === 'completed'" class="p-1">
                  <div class="small"><strong>Diag:</strong> {{ appt.diagnosis }}</div>
                  <div class="small text-muted"><strong>RX:</strong> {{ appt.prescription }}</div>
                </div>
                <div v-else class="text-muted small fst-italic">Waiting for checkup...</div>
              </td>
              <td>
                <div v-if="appt.status === 'pending'" class="d-flex gap-1">
                  <button @click="openReschedule(appt)" class="btn btn-sm btn-outline-primary">
                    Reschedule
                  </button>
                  <button @click="cancelAppointment(appt.id)" class="btn btn-sm btn-danger">
                    Cancel
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="my_appts.length === 0">
              <td colspan="5" class="text-center py-5 text-muted">No appointments booked yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="rescheduleAppt" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment #{{ rescheduleAppt.id }}</h5>
            <button type="button" class="btn-close" @click="rescheduleAppt = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-bold">New Date</label>
              <input type="date" class="form-control" v-model="newDate" :min="minDate" @change="fetchSlots">
            </div>
            <div v-if="newDate && slots.length > 0" class="mb-3">
              <label class="form-label small fw-bold">New Time Slot</label>
              <div class="d-flex flex-wrap gap-2">
                <button v-for="s in slots" :key="s" type="button"
                  :class="['btn btn-sm', newTime === s ? 'btn-primary' : 'btn-outline-primary']" @click="newTime = s">{{
                    s }}</button>
              </div>
            </div>
            <p v-if="newDate && slots.length === 0" class="text-danger small">No slots available for this date.</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary btn-sm" @click="rescheduleAppt = null">Close</button>
            <button class="btn btn-primary btn-sm" :disabled="!newTime" @click="confirmReschedule">Confirm</button>
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

const my_appts = ref([]);
const rescheduleAppt = ref(null);
const newDate = ref('');
const newTime = ref('');
const slots = ref([]);
const minDate = new Date().toISOString().split('T')[0];

const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/patient/appointments');
    my_appts.value = res.data;
  } catch (err) {
    notify.error('Failed to fetch appointments');
  }
};

onMounted(fetchAppointments);

const cancelAppointment = async (apptId) => {
  if (!confirm('Cancel this appointment?')) return;
  try {
    await axios.put(`/api/patient/cancel-appointment/${apptId}`);
    notify.success('Appointment cancelled');
    await fetchAppointments();
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Failed to cancel');
  }
};

const triggerExport = async () => {
  try {
    notify.info('Preparing your export...');
    const res = await axios.post('/api/patient/export-treatments');
    notify.success(res.data.msg);
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Export failed');
  }
};

const openReschedule = (appt) => {
  rescheduleAppt.value = appt;
  newDate.value = '';
  newTime.value = '';
  slots.value = [];
};

const fetchSlots = async () => {
  if (!newDate.value) return;
  slots.value = [];
  newTime.value = '';

  const appt = my_appts.value.find(a => a.id === rescheduleAppt.value.id);
  if (!appt) return;

  try {
    const res = await axios.post('/api/patient/get-available-slots', {
      doct_id: appt.doctor_id,
      date: newDate.value
    });
    slots.value = Array.isArray(res.data) ? res.data : [];
  } catch (err) {
    const msg = err.response?.data?.msg || 'Could not fetch slots';
    notify.error(msg);
  }
};

const confirmReschedule = async () => {
  if (!newDate.value || !newTime.value) return;
  try {
    await axios.put(`/api/patient/reschedule-appointment/${rescheduleAppt.value.id}`, {
      date: newDate.value,
      time: newTime.value
    });
    notify.success('Appointment rescheduled');
    rescheduleAppt.value = null;
    await fetchAppointments();
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Reschedule failed');
  }
};
</script>