<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-12 col-sm-10 col-md-6 col-lg-5">
        <div class="card shadow-sm border-0 p-4 p-md-4">
          <div class="text-center mb-4">
            <h3 class="fw-bold mb-1 text-primary">Welcome Back</h3>
            <p class="text-muted mb-0 small">Sign in to continue</p>
          </div>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label small fw-bold">Username</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-person text-primary"></i></span>
                <input v-model="username" type="text" class="form-control" placeholder="Enter username"
                  autocomplete="username" required />
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label small fw-bold">Password</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-lock text-primary"></i></span>
                <input v-model="password" type="password" class="form-control" placeholder="••••••••"
                  autocomplete="current-password" required />
              </div>
            </div>

            <button type="submit" class="btn btn-primary w-100 fw-bold shadow-sm py-2" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
              {{ isLoading ? 'Signing In...' : 'Sign In' }}
            </button>

            <p class="text-center mt-3 mb-0 small">
              Don't have an account?
              <router-link to="/signup" class="fw-bold text-decoration-none">Create account</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store';
import { useRouter } from 'vue-router';
import { notify } from '../ui/notify';

const username = ref("");
const password = ref("");
const auth = useAuthStore();
const router = useRouter();
const isLoading = ref(false);


onMounted(() => {
  if (auth.token) {
    auth.logout();
  }
});

const handleLogin = async () => {
  if (isLoading.value) return;
  isLoading.value = true;

  try {
    const res = await axios.post("/api/auth/login", {
      username: username.value,
      password: password.value
    });
    auth.login(res.data.access_token, res.data.role, res.data.name);
    notify.success("Login Successful!");

    const role = auth.role;
    if (role === 'admin') router.push('/admin');
    else if (role === 'doctor') router.push('/doctor');
    else router.push('/patient');
  } catch (error) {
    notify.error(error.response?.data?.msg || "Login failed");
  } finally {
    isLoading.value = false;
  }
};
</script>