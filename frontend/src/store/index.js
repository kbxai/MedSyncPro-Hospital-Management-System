import { defineStore } from 'pinia'; 


export const useAuthStore = defineStore('auth',{
    state: () => ({
        token: localStorage.getItem('access_token') || null,
        role: localStorage.getItem('role') || null,
        name : localStorage.getItem('user_name') || null,
}),
    actions: {
        login(token,role,name){
            this.token = token;
            this.role = role;
            this.name = name;
            localStorage.setItem('access_token', token);
            localStorage.setItem('role', role);
            localStorage.setItem('user_name', name);
        },
        logout(){
            this.token = null;
            this.role = null;
            this.name = null;
            localStorage.removeItem('access_token');
            localStorage.removeItem('role');
            localStorage.removeItem('user_name');
        }
    }
});
