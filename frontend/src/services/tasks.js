import { tasksClient } from './api';

export const tasksAPI = {
    getAll: () => tasksClient.get('/tasks/public').then(r => r.data),
    getCourses: () => tasksClient.get('/courses/public').then(r => r.data),
    createCourse: (data) => tasksClient.post('/courses/', data).then(r => r.data),
    createTask: (data) => tasksClient.post('/tasks/', data).then(r => r.data),
    deleteTask: (id) => tasksClient.delete(`/tasks/${id}`).then(r => r.data),
};
