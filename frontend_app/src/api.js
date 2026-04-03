import axios from 'axios';

const api = axios.create({
  baseURL: 'https://sheildrun-production.up.railway.app',
  timeout: 10000,
});

export default api;
