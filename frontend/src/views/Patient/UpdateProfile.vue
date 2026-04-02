<template>
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-12 col-sm-10 col-md-6 col-lg-5">
                <div class="card shadow-sm border-0 p-4 p-md-4">
                    <div class="text-center mb-4">
                        <h3 class="fw-bold mb-1 text-primary">Update profile</h3>
                        <p class="text-muted mb-0 small">Update your profile to continue</p>
                    </div>

                    <form @submit.prevent="UpdatePatient">
                        <div class="mb-3">
                            <label class="form-label small fw-bold">Full Name</label>
                            <input type="text" class="form-control" v-model="form.name" required>
                        </div>

                        <div class="row g-3">
                            <div class="col-12 col-md-6">
                                <label class="form-label small fw-bold">Age</label>
                                <input type="number" class="form-control" v-model="form.age" required>
                            </div>
                            <div class="col-12 col-md-6">
                                <label class="form-label small fw-bold">Gender</label>
                                <select class="form-select" v-model="form.gender" required>
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                        </div>

                        <div class="mb-3 mt-3">
                            <label class="form-label small fw-bold">Username</label>
                            <input type="text" class="form-control" v-model="form.username" disabled>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold shadow-sm py-2">
                            Update Account
                        </button>

                        <p class="text-center mt-3 mb-0 small"><router-link to="/patient">Back to
                                Dashboard</router-link>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { notify } from '../../ui/notify';

const router = useRouter();
const form = reactive({
    id: null, username: '', name: '', age: '', gender: ''
});


onMounted(async () => {
    try {
        const tokenRes = await axios.post('/api/patient/get-patient-by-token/');
        const patId = tokenRes.data.id;

        if (!patId) {
            notify.error('Could not identify patient');
            router.push('/patient');
            return;
        }


        const res = await axios.get(`/api/patient/update-patient/${patId}`);
        const data = res.data;

        form.id = patId;
        form.username = data.username ?? '';
        form.name = data.name ?? '';
        form.age = data.age ?? '';
        form.gender = data.gender ?? '';
    } catch (err) {
        notify.error(err.response?.data?.msg || 'Failed to load patient data');
        router.push('/patient');
    }
});

const UpdatePatient = async () => {
    try {
        if (!form.id) {
            notify.error('No patient ID - cannot update');
            return;
        }
        const payload = {
            name: form.name,
            age: Number(form.age),
            gender: form.gender
        };
        await axios.put(`/api/patient/update-patient/${form.id}`, payload);
        notify.success('patient updated successfully!');
        router.push('/patient');
    } catch (err) {

        notify.error(err.response?.data?.msg || err.message || 'Update failed');
    }
};
</script>