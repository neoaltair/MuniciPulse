/**
 * API utilities for making requests to the backend
 */
import axios from 'axios';
import { getToken } from './auth';

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Create axios instance with default config
 */
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Add authorization header to requests if token exists
 */
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Handle response errors
 */
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('civicfix_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;

/**
 * Auth API endpoints
 */
export const authAPI = {
    register: (userData) => api.post('/auth/register', userData),
    login: (credentials) => api.post('/auth/login', credentials),
    getMe: () => api.get('/auth/me'),
};

/**
 * Reports API endpoints
 */
export const reportsAPI = {
    create: (formData) => api.post('/reports', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    getAll: (params) => api.get('/reports', { params }),
    getPublic: (params) => api.get('/reports/public', { params }),
    getById: (id) => api.get(`/reports/${id}`),
    updateStatus: (id, formData) => api.patch(`/reports/${id}/status`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    getLinked: (id) => api.get(`/reports/${id}/linked`),
};
