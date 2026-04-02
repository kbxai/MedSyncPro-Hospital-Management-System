<template>
    <div class="mt-4">
        <h3>Update Doctor</h3>
        <form @submit.prevent="updateDoctor">
            <input v-model="formData.username" class="form-control mb-2" placeholder="Username" disabled>
            <input v-model="formData.name" class="form-control mb-2" placeholder="Full Name" required>

            <select v-model="formData.dept_id" class="form-select mb-2" required>
                <option value="">Select Dept</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }} </option>
            </select>

            <input v-model="formData.availability" class="form-control mb-2" placeholder="Mon,Tue|09:00-17:00" required>

            <button type="submit" class="btn btn-success w-100">Update Doctor</button>
        </form>
    </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { notify } from '../../ui/notify';

const departments = ref([]);
const router = useRouter();
const route = useRoute();
const formData = reactive({
    id: null, username: '', name: '', dept_id: '', availability: ''
});


onMounted(async () => {
    try {
        const res = await axios.get('/api/admin/get-departments');
        departments.value = res.data;
    } catch (err) {
        notify.error('Failed to load departments');
    }

    try {
        const doctorId = route.query.id;
        if (!doctorId) {
            notify.error('No doctor ID provided');
            router.push('/admin/view-doctors');
            return;
        }
        const res = await axios.get(`/api/admin/get-doctor/${doctorId}`);
        const data = res.data;

        formData.id = doctorId;
        formData.username = data.username ?? '';
        formData.name = data.name ?? '';
        formData.dept_id = data.dept_id ?? '';
        formData.availability = data.availability ?? '';
    } catch (err) {
        notify.error(err.response?.data?.msg || 'Failed to load doctor data');
    }
});

import { normalizeAvailability } from '../../utils/availability';

const updateDoctor = async () => {
    try {
        if (!formData.id) {
            notify.error('No doctor ID - cannot update');
            return;
        }
        const payload = {
            name: formData.name,
            dept_id: Number(formData.dept_id),
            availability: normalizeAvailability(formData.availability)
        };


        await axios.put(`/api/admin/update-doctor/${formData.id}`, payload);
        notify.success('Doctor updated successfully!');
        router.push('/admin/view-doctors');
    } catch (err) {

        notify.error(err.response?.data?.msg || err.message || 'Update failed');
    }
};
</script>