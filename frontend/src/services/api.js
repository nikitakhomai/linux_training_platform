import axios from 'axios';

const API_BASE_URL = 'http://localhost';

export const authClient = axios.create({
    baseURL: `${API_BASE_URL}:8000`,
    timeout: 30000,
});

export const tasksClient = axios.create({
    baseURL: `${API_BASE_URL}:8001`,
    timeout: 30000,
});

export const orchestrationClient = axios.create({
    baseURL: `${API_BASE_URL}:8003`,
    timeout: 30000,
});

export const checkClient = axios.create({
    baseURL: `${API_BASE_URL}:8002`,
    timeout: 30000,
});

const addAuthInterceptor = (client) => {
    client.interceptors.request.use((config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    });
};

addAuthInterceptor(authClient);
addAuthInterceptor(tasksClient);
addAuthInterceptor(orchestrationClient);
addAuthInterceptor(checkClient);
