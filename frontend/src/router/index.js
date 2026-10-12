import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Signup from '../views/Signup.vue';
import AdminDashboard from '../views/Admin/AdminDashboard.vue';
import ManageDepartments from '../views/Admin/ManageDepartments.vue';
import AddDoctor from '../views/Admin/AddDoctor.vue';
import ViewDoctors from '../views/Admin/ViewDoctors.vue';
import SearchDoctors from '../views/Admin/SearchDoctors.vue';
import SearchPatients from '../views/Admin/SearchPatients.vue';
import ViewAppointments from '../views/Admin/ViewAppointments.vue';
import DoctorDashboard from '../views/Doctor/DoctorDashboard.vue';
import AddTreatment from '../views/Doctor/AddTreatment.vue';
import PatientDashboard from '../views/Patient/PatientDashboard.vue';
import BookAppointment from '../views/Patient/BookAppointment.vue';
import MyAppointments from '../views/Patient/MyAppointments.vue';
import UpdateDoctor from '../views/Admin/UpdateDoctor.vue';
import { notify } from '../ui/notify';
import PatientHistory from '@/views/Doctor/PatientHistory.vue';
import UpdateProfile from '@/views/Patient/UpdateProfile.vue';
import UpdateAvailability from '@/views/Doctor/UpdateAvailability.vue';
import SetPassword from '../views/SetPassword.vue';

const routes = [
  { path: '/login', component: Login },
  { path: '/signup', component: Signup },
  { path: '/set-password', component: SetPassword },
  
  { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/view-doctors', component: ViewDoctors, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/add-doctor', component: AddDoctor, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/departments', component: ManageDepartments, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/search-doctors', component: SearchDoctors, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/search-patients', component: SearchPatients, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/appointments', component: ViewAppointments, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/update-doctor', component: UpdateDoctor, meta: { requiresAuth: true, role: 'admin' } },



  { path: '/doctor', component: DoctorDashboard, meta: { requiresAuth: true, role: 'doctor' } },
  { path: '/doctor/add-treatment', component: AddTreatment, meta: { requiresAuth: true, role: 'doctor' } },
  { path: '/doctor/patient-history', component: PatientHistory, meta: { requiresAuth: true, role: 'doctor' } },
  { path: '/doctor/update-availability', component: UpdateAvailability, meta: { requiresAuth: true, role: 'doctor' } },


  { path: '/patient', component: PatientDashboard, meta: { requiresAuth: true, role: 'patient' } },
  { path: '/patient/book', component: BookAppointment, meta: { requiresAuth: true, role: 'patient' } },
  { path: '/patient/appointments', component: MyAppointments, meta: { requiresAuth: true, role: 'patient' } },
  { path: '/patient/update-profile', component: UpdateProfile, meta: { requiresAuth: true, role: 'patient' } },
  
  { path: '/', redirect: '/login' }

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');

  if (to.meta.requiresAuth) {
    if (!token) return next('/login');

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const role = payload.role;

      if (payload.exp && payload.exp * 1000 < Date.now()) {
        localStorage.clear();
        return next('/login');
      }

      if (to.meta.role && to.meta.role !== role) {
        notify.error("Unauthorized Access!");
        return next('/login');
      }
      next();
    } catch (e) {
      localStorage.clear();
      next('/login');
    }
  } else {
    next();
  }
});

export default router;