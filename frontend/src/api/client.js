import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

export const searchAssets = async (params = {}) => {
  const { q = '', type = 'all', limit = 30, sort = 'relevance' } = params;
  const response = await api.get('/search', {
    params: { q, type, limit, sort }
  });
  return response.data;
};

export const startIndexing = async () => {
  const response = await api.post('/index/start');
  return response.data;
};

export const getIndexingStatus = async () => {
  const response = await api.get('/index/status');
  return response.data;
};

export const resetIndex = async () => {
  const response = await api.delete('/index/reset');
  return response.data;
};

export const getAssetPreview = async (assetId) => {
  const response = await api.get(`/preview/${assetId}`);
  return response.data;
};

export const getSystemStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export default api;
