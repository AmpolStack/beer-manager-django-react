import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const brandApi = {
  list: (params) => api.get('/brands/', { params }),
  get: (id) => api.get(`/brands/${id}/`),
  create: (data) => api.post('/brands/', data),
  update: (id, data) => api.put(`/brands/${id}/`, data),
  partialUpdate: (id, data) => api.patch(`/brands/${id}/`, data),
  delete: (id) => api.delete(`/brands/${id}/`),
  getBeers: (id) => api.get(`/brands/${id}/beers/`),
};

export const beerApi = {
  list: (params) => api.get('/beers/', { params }),
  get: (id) => api.get(`/beers/${id}/`),
  create: (data) => api.post('/beers/', data),
  update: (id, data) => api.put(`/beers/${id}/`, data),
  partialUpdate: (id, data) => api.patch(`/beers/${id}/`, data),
  delete: (id) => api.delete(`/beers/${id}/`),
  getTypes: () => api.get('/beers/types/'),
};

export default api;