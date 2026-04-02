import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import { createPinia } from 'pinia';
import axios from 'axios';
import { notify } from './ui/notify';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.clear();
      router.push('/login');
      notify.error('Session expired. Please login again.');
    } else if (error.response?.status === 403) {
      notify.error('Access denied. Insufficient permissions.');
    }
    return Promise.reject(error);
  }
);

const app = createApp(App)
app.use(createPinia());
app.use(router);
app.mount('#app')