<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <div class="brand-icon me-2">
          <i class="bi bi-heart-pulse-fill text-primary fs-3"></i>
        </div>
        <span class="fw-bold tracking-tight text-dark">MedSync<span class="text-primary">Pro</span></span>
      </router-link>
      
      <div class="ms-auto d-flex align-items-center">
        <div v-if="!auth.token">
          <router-link class="btn btn-link text-decoration-none text-dark me-3 fw-semibold" to="/login">Sign In</router-link>
          <router-link class="btn btn-primary shadow-sm" to="/signup">Get Started</router-link>
        </div>
        <div v-else class="dropdown">
          <button class="btn btn-light dropdown-toggle d-flex align-items-center" data-bs-toggle="dropdown">
            <i class="bi bi-person-circle fs-5 me-2 text-primary"></i>
            <span class="small fw-bold text-uppercase">{{ auth.name || auth.role }}</span>
          </button>
          <ul class="dropdown-menu dropdown-menu-end border-0 shadow mt-2">
            <li><button class="dropdown-item text-danger" @click="handleLogout"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from "../store";
import { useRouter } from "vue-router";
import { notify } from '../ui/notify';


const auth = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  auth.logout();
  notify.success("Logout Successful!");
  router.push("/login");
};
</script>
