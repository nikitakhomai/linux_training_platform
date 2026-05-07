import { authClient } from './api';

export const authAPI = {
    register: (email, username, password, role) =>
        authClient.post('/auth/register', { email, username, password, role }).then(r => r.data),

    login: (username, password) =>
        authClient.post('/auth/login', new URLSearchParams({ username, password }), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        }).then(r => r.data),

    getMe: () =>
        authClient.get('/users/me').then(r => r.data),
};
