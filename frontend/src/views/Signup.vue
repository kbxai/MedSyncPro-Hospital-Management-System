<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-5">
        <div class="card shadow-sm border-0 p-4 p-md-4">
          <div class="text-center mb-4">
            <h3 class="fw-bold mb-1 text-primary">Patient Registration</h3>
            <p class="text-muted mb-0 small">Create your account to continue</p>
          </div>

          <form @submit.prevent="handleSignup" novalidate>
            <div class="mb-3">
              <label class="form-label small fw-bold">Full Name</label>
              <input type="text" class="form-control" :class="{ 'is-invalid': errors.name }" v-model="form.name" required>
              <div class="invalid-feedback">{{ errors.name }}</div>
            </div>

            <div class="row g-3">
              <div class="col-12 col-md-6">
                <label class="form-label small fw-bold">Age</label>
                <input type="number" class="form-control" :class="{ 'is-invalid': errors.age }" v-model="form.age"
                  required>
                <div class="invalid-feedback">{{ errors.age }}</div>
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
              <input type="text" class="form-control" :class="{ 'is-invalid': errors.username }" v-model="form.username"
                required>
              <div class="invalid-feedback">{{ errors.username }}</div>
            </div>

            <div class="mb-4">
              <label class="form-label small fw-bold">Password</label>
              <input type="password" class="form-control" :class="{ 'is-invalid': errors.password }"
                v-model="form.password" required>
              <div class="invalid-feedback">{{ errors.password }}</div>
            </div>

            <button type="submit" class="btn btn-primary w-100 fw-bold shadow-sm py-2" :disabled="isLoading">
              Create Account
            </button>

            <p class="text-center mt-3 mb-0 small">
              Already have an account? <router-link to="/login">Login here</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store';
import { notify } from '../ui/notify';

const form = reactive({ name: '', age: '', gender: 'Male', username: '', password: '' });
const errors = reactive({ name: '', age: '', username: '', password: '' });
const router = useRouter();
const auth = useAuthStore();
const isLoading = ref(false);

onMounted(() => {
  if (auth.token) {
    auth.logout();
  }
});

const validate = () => {
  let valid = true;
  errors.name = '';
  errors.age = '';
  errors.username = '';
  errors.password = '';

  if (!form.name || form.name.trim().length < 2) {
    errors.name = 'Name must be at least 2 characters';
    valid = false;
  }

  const age = Number(form.age);
  if (!form.age || age < 1 || age > 120) {
    errors.age = 'Age must be between 1 and 120';
    valid = false;
  }

  if (!form.username || form.username.trim().length < 3) {
    errors.username = 'Username must be at least 3 characters';
    valid = false;
  }

  if (!form.password || form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
    valid = false;
  } else if (!/[A-Z]/.test(form.password)) {
    errors.password = 'Password must contain uppercase letter';
    valid = false;
  } else if (!/[0-9]/.test(form.password)) {
    errors.password = 'Password must contain number';
    valid = false;
  } else if (!/[!@#$%^&*]/.test(form.password)) {
    errors.password = 'Password must contain special character';
    valid = false;
  }

  return valid;
};

const handleSignup = async () => {
  if (!validate()) return;
  if (isLoading.value) return;
  isLoading.value = true;

  try {
    await axios.post('/api/auth/signup', form);
    notify.success("Registration Successful! Please login.");
    router.push('/login');
  } catch (err) {
    notify.error(err.response?.data?.msg || "Signup failed");
  } finally {
    isLoading.value = false;
  }
};
</script>