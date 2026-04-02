<template>
  <div id="app">
    <Navbar />
    <NotificationHost />
    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import NotificationHost from './components/NotificationHost.vue';
</script>



<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #0d6efd;
  --bg-soft: #f8fafc;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-soft);
  color: #1e293b;
}

h1,
h2,
h3,
.navbar-brand {
  font-family: 'Poppins', sans-serif;
}

.card {
  border: none !important;
  border-radius: 12px !important;
  transition: transform 0.2s ease;
  background-color: var(--bg-soft);
}

.card:hover {
  transform: translateY(-3px);
}

.btn-primary {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
}
</style>