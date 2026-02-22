/**
 * API Service
 * Handles all backend API calls
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Intake API
export const intakeAPI = {
  submitIntake: (data) => api.post('/api/intake/submit', data),
  chatMessage: (message, history) => 
    api.post('/api/intake/chat', { 
      user_message: message, 
      conversation_history: history 
    }),
  getPatientIntake: (patientId) => api.get(`/api/intake/patient/${patientId}`),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/api/admin/dashboard'),
  getHighRiskPatients: (limit = 20) => 
    api.get(`/api/admin/high-risk-patients?limit=${limit}`),
  getAlerts: (severity = null, limit = 50) => {
    const params = new URLSearchParams({ limit });
    if (severity) params.append('severity', severity);
    return api.get(`/api/admin/alerts?${params}`);
  },
  acknowledgeAlert: (alertId, acknowledgedBy) => 
    api.post(`/api/admin/alerts/${alertId}/acknowledge`, { acknowledged_by: acknowledgedBy }),
  resolveAlert: (alertId, notes) => 
    api.post(`/api/admin/alerts/${alertId}/resolve`, { resolution_notes: notes }),
  getTherapistCaseloads: () => api.get('/api/admin/therapists/caseloads'),
  assignPatient: (patientId, therapistId, assignedBy) => 
    api.post('/api/admin/assign-patient', {
      patient_id: patientId,
      therapist_id: therapistId,
      assigned_by: assignedBy
    }),
};

// Matching API
export const matchingAPI = {
  getRecommendations: (patientId, topN = 3) => 
    api.post('/api/matching/recommend', { 
      patient_id: patientId, 
      top_n: topN 
    }),
  assignTherapist: (patientId, therapistId, matchScore, reasoning) => 
    api.post('/api/matching/assign', {
      patient_id: patientId,
      therapist_id: therapistId,
      match_score: matchScore,
      match_reasoning: reasoning
    }),
  checkAvailability: (filters = {}) => {
    const params = new URLSearchParams(filters);
    return api.get(`/api/matching/availability?${params}`);
  },
};

export default api;
