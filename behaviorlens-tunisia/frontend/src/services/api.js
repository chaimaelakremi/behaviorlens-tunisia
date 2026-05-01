import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const auth = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
}

export const core = {
  stats: () => api.get('/stats'),
  statsByRegion: () => api.get('/stats/by-region'),
  statsByModule: () => api.get('/stats/by-module'),
  statsByAge: () => api.get('/stats/by-age'),
  timeline: (days = 30) => api.get(`/stats/timeline?days=${days}`),
  modules: () => api.get('/modules'),
  collect: (data) => api.post('/collect', data),
}

export const social = {
  collect: (data) => api.post('/social/collect', data),
  trends: () => api.get('/social/trends'),
  sentiment: () => api.get('/social/sentiment'),
  stats: () => api.get('/social/stats'),
}

export const terrain = {
  submit: (data) => api.post('/terrain/submit', data),
  agents: () => api.get('/terrain/agents'),
  sync: () => api.get('/terrain/sync'),
  stats: () => api.get('/terrain/stats'),
}

export const ivr = {
  createCampaign: (data) => api.post('/ivr/campaign', data),
  recordResponse: (data) => api.post('/ivr/response', data),
  results: (id) => api.get(`/ivr/results/${id}`),
  stats: () => api.get('/ivr/stats'),
}

export const commerce = {
  registerStore: (data) => api.post('/commerce/store', data),
  submitSale: (data) => api.post('/commerce/sale', data),
  topProducts: () => api.get('/commerce/top-products'),
  byRegion: () => api.get('/commerce/by-region'),
  stats: () => api.get('/commerce/stats'),
}

export const gamification = {
  play: (data) => api.post('/game/play', data),
  games: () => api.get('/game/list'),
  reward: (data) => api.post('/game/reward', data),
  leaderboard: () => api.get('/game/leaderboard'),
  stats: () => api.get('/game/stats'),
}

export const opendata = {
  fetch: (source) => api.get(`/opendata/fetch?source=${source}`),
  stats: () => api.get('/opendata/stats'),
  import: (data) => api.post('/opendata/import', data),
}

export const mood = {
  record: (data) => api.post('/mood/record', data),
  map: () => api.get('/mood/map'),
  trends: (days = 30) => api.get(`/mood/trends?days=${days}`),
  byRegion: () => api.get('/mood/by-region'),
  stats: () => api.get('/mood/stats'),
}

export const photo = {
  submit: (data) => api.post('/photo/submit-json', data),
  challenges: () => api.get('/photo/challenges'),
  stats: () => api.get('/photo/stats'),
}

export default api
