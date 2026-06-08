import axios from 'axios';
import type { MedicalDocument, RAGQuery, SystemStats } from '../types';

export type { MedicalDocument, RAGQuery, SystemStats };

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: string;
  department?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
    full_name?: string;
    role: string;
    department?: string;
  };
}

export const authAPI = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

export interface DocumentListResponse {
  documents: MedicalDocument[];
  total: number;
  page: number;
  page_size: number;
}

export const documentAPI = {
  getAll: async (page = 1, pageSize = 10, category?: string, search?: string): Promise<DocumentListResponse> => {
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (category) params.category = category;
    if (search) params.search = search;
    const response = await api.get('/documents', { params });
    return response.data;
  },

  getById: async (id: string): Promise<MedicalDocument> => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  create: async (document: Omit<MedicalDocument, 'id' | 'created_at' | 'updated_at' | 'status' | 'chunk_count' | 'file_type' | 'file_size'>): Promise<MedicalDocument> => {
    const response = await api.post('/documents', document);
    return response.data;
  },

  update: async (id: string, document: Partial<MedicalDocument>): Promise<MedicalDocument> => {
    const response = await api.put(`/documents/${id}`, document);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  search: async (query: string): Promise<DocumentListResponse> => {
    const response = await api.get('/documents', { params: { search: query } });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/documents/stats/overview');
    return response.data;
  },

  upload: async (formData: FormData): Promise<MedicalDocument> => {
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};

export const ragAPI = {
  query: async (query: string, topK = 5, retrievalMode = 'hybrid'): Promise<RAGQuery> => {
    const response = await api.post('/rag/query', {
      query,
      top_k: topK,
      retrieval_mode: retrievalMode
    });
    return response.data;
  },

  getHistory: async (limit = 20): Promise<{ queries: RAGQuery[]; total: number }> => {
    const response = await api.get('/rag/history', { params: { limit } });
    return response.data;
  },

  getStats: async (): Promise<SystemStats> => {
    const response = await api.get('/rag/stats');
    return response.data;
  },

  submitFeedback: async (queryLogId: number, rating: string, comment?: string, correctedResponse?: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/rag/feedback', {
      query_log_id: queryLogId,
      rating,
      comment,
      corrected_response: correctedResponse
    });
    return response.data;
  }
};

export const systemAPI = {
  getHealth: async (): Promise<{ status: string; timestamp: string; version: string }> => {
    const response = await api.get('/system/health');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/system/metrics');
    return response.data;
  }
};

export default api;
