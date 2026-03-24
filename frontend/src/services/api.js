import axios from 'axios';

// This tells Vite: "Use the Vercel variable if it exists, otherwise fallback to localhost for local testing"
const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_LOCAL_API_URL || 'http://localhost:8080/api';


const api = axios.create({
  baseURL: API_BASE_URL,
});

export const analyzeResume = async (file, jdText) => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('jd', jdText);

  const response = await api.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const rankCandidates = async (files, jdText) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  formData.append('jd', jdText);

  const response = await api.post('/rank', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const generateIdealResume = async (jdText) => {
  const formData = new FormData();
  formData.append('jd', jdText);

  const response = await api.post('/generate-ideal-resume', formData);
  return response.data;
};

export default api;
