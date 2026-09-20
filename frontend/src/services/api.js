import axios from 'axios'

/**
 * Axios instance pre-configured with the backend base URL.
 * Falls back to localhost:8000 for local development.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// ── Request Interceptor ─────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('feeassist_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor ────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If we get an unauthorized error on a protected route, clean up local state
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        localStorage.removeItem('feeassist_token')
        localStorage.removeItem('feeassist_user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Auth Endpoints ───────────────────────────────────────────────────────────
export const authService = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
}

// ── Fee Endpoints ────────────────────────────────────────────────────────────
export const feesService = {
  getFees: () => api.get('/api/fees'),
  getSummary: () => api.get('/api/fees/summary'),
}

// ── Payment Endpoints ────────────────────────────────────────────────────────
export const paymentsService = {
  getPayments: () => api.get('/api/payments'),
}

// ── Chat Endpoints ───────────────────────────────────────────────────────────
export const chatService = {
  sendMessage: (data) => api.post('/api/chat/message', data),
  getHistory: () => api.get('/api/chat/history'),
}

export default api
