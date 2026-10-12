<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-5">
        <div class="card shadow-sm border-0 p-4">
          <h3 class="fw-bold mb-3 text-primary">Set your password</h3>
          <form @submit.prevent="submit">
            <label class="form-label small fw-bold">New password</label>
            <input v-model="password" type="password" class="form-control mb-3" autocomplete="new-password" required>
            <button class="btn btn-primary w-100" :disabled="loading">
              {{ loading ? 'Saving...' : 'Save password' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { notify } from '../ui/notify';

const route = useRoute();
const router = useRouter();
const password = ref('');
const loading = ref(false);

const submit = async () => {
  if (loading.value) return;
  loading.value = true;
  try {
    await axios.post('/api/auth/set-password', {
      token: route.query.token,
      password: password.value
    });
    notify.success('Password saved. You can now sign in.');
    router.push('/login');
  } catch (error) {
    notify.error(error.response?.data?.msg || 'Unable to set password');
  } finally {
    loading.value = false;
  }
};
</script>
