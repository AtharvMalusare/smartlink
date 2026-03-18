import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

export const createLink = (data) => api.post('/links', data)
export const checkSlug = (slug) => api.get(`/check/${slug}`)
export const addRule = (shortCode, token, rule) =>
  api.post(`/links/${shortCode}/rules?token=${token}`, rule)
export const getRules = (shortCode, token) =>
  api.get(`/links/${shortCode}/rules?token=${token}`)
export const deleteRule = (ruleId, token) =>
  api.delete(`/rules/${ruleId}?token=${token}`)
export const getAnalytics = (shortCode, token) =>
  api.get(`/links/${shortCode}/analytics?token=${token}`)
export const deleteLink = (shortCode, token) =>
  api.delete(`/links/${shortCode}?token=${token}`)