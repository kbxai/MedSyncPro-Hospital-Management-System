<template>
  <div class="mt-4">
    <h3>Add Doctor</h3>
    <form @submit.prevent="registerDoctor">
      <input v-model="formData.username" class="form-control mb-2" placeholder="Username" required>
      <input v-model="formData.password" type="password" class="form-control mb-2" placeholder="Password" required>
      <input v-model="formData.name" class="form-control mb-2" placeholder="Full Name" required>

      <select v-model="formData.dept_id" class="form-select mb-2" required>
        <option value="">Select Dept</option>
        <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>

      <input v-model="formData.availability" class="form-control mb-2" placeholder="Mon,Tue|09:00-17:00" required>

      <button type="submit" class="btn btn-success w-100">Register</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';

const departments = ref([]);
const router = useRouter();
const formData = reactive({
  username: '', password: '', name: '', dept_id: '', availability: ''
});

onMounted(async () => {
  try {
    const res = await axios.get('/api/admin/get-departments');
    departments.value = res.data;
  } catch (err) {
    notify.error(err.response?.data?.msg || 'Failed to load departments');
  }
});

import { normalizeAvailability } from '../../utils/availability';

const validatePassword = (pw) => {
  if (!pw || pw.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Z]/.test(pw)) return 'Password must contain uppercase letter';
  if (!/[0-9]/.test(pw)) return 'Password must contain number';
  if (!/[!@#$%^&*]/.test(pw)) return 'Password must contain special character';
  return null;
};

const registerDoctor = async () => {
  const pwError = validatePassword(formData.password);
  if (pwError) { notify.error(pwError); return; }
  try {
    formData.availability = normalizeAvailability(formData.availability);
    await axios.post('/api/admin/add-doctor', formData);
    notify.success('Doctor added successfully!');
    router.push('/admin/view-doctors');
  } catch (err) {
    notify.error(err.response?.data?.msg || err.message || 'Registration failed');
  }
};
</script>