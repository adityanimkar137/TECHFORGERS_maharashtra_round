import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// VITE_USE_MOCK=true uses built-in demo data; false calls the FastAPI backend.
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

// Sidebar / dashboard shortcuts. Mock mode has fixed demo runs; real mode has none, so go to the failed-run list.
export const links = USE_MOCK
  ? { diagnose: '/runs/RUN-1024/diagnosis', replay: '/runs/RUN-1024/replay', compare: '/comparison/RUN-1024/RUN-1031' }
  : { diagnose: '/runs?status=FAILED', replay: '/runs?status=FAILED', compare: '/runs?status=FAILED' }

const api = axios.create({ baseURL: API_URL, timeout: 15000 })
api.interceptors.response.use(
  (r) => r,
  (err) => {
    err.message = err.response?.data?.detail
      || (err.code === 'ERR_NETWORK' ? `Cannot reach the backend at ${API_URL}. Check that it is running and that CORS is enabled.` : err.message)
    return Promise.reject(err)
  }
)

export const delay = (ms = 400) => new Promise((r) => setTimeout(r, ms))
export default api
