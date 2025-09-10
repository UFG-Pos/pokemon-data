import axios from 'axios';
import type {
  ApiResponse,
  HealthStatus,
  PokemonListResponse,
  PipelineStatusResponse,
  EventsResponse,
  AlertsResponse,
  DashboardResponse,
  FileOperationResponse,
  CleanDataResponse,
  ReportResponse,
  Pokemon,
} from '../types/api';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health API
export const healthApi = {
  getHealth: (): Promise<HealthStatus> =>
    api.get('/api/v1/health').then((res) => res.data),
};

// Pokemon API
export const pokemonApi = {
  importPokemon: (name: string): Promise<ApiResponse<Pokemon>> =>
    api.get(`/api/v1/import-pokemon?name=${encodeURIComponent(name)}`).then((res) => res.data),

  listPokemons: (skip = 0, limit = 20): Promise<PokemonListResponse> =>
    api.get(`/api/v1/pokemons?skip=${skip}&limit=${limit}`).then((res) => res.data),

  getPokemonByName: (name: string): Promise<ApiResponse<Pokemon>> =>
    api.get(`/api/v1/pokemons/${encodeURIComponent(name)}`).then((res) => res.data),
};

// Pipeline API
export const pipelineApi = {
  // Status
  getStatus: (): Promise<PipelineStatusResponse> =>
    api.get('/api/v1/pipeline/status').then((res) => res.data),

  // Stream Processing
  startStream: (): Promise<ApiResponse> =>
    api.post('/api/v1/pipeline/stream/start').then((res) => res.data),

  stopStream: (): Promise<ApiResponse> =>
    api.post('/api/v1/pipeline/stream/stop').then((res) => res.data),

  getEvents: (limit = 50): Promise<EventsResponse> =>
    api.get(`/api/v1/pipeline/stream/events?limit=${limit}`).then((res) => res.data),

  simulateAnomaly: (pokemonName: string, anomalyType: string): Promise<ApiResponse> =>
    api.post(`/api/v1/pipeline/stream/simulate-anomaly?pokemon_name=${encodeURIComponent(pokemonName)}&anomaly_type=${anomalyType}`).then((res) => res.data),

  // File Operations
  exportCSV: (): Promise<FileOperationResponse> =>
    api.post('/api/v1/pipeline/file/export-csv').then((res) => res.data),

  exportJSON: (): Promise<FileOperationResponse> =>
    api.post('/api/v1/pipeline/file/export-json').then((res) => res.data),

  cleanData: (): Promise<CleanDataResponse> =>
    api.post('/api/v1/pipeline/file/clean-data').then((res) => res.data),

  // Dashboard
  getDashboardData: (): Promise<DashboardResponse> =>
    api.get('/api/v1/pipeline/dashboard/data').then((res) => res.data),

  generateReport: (reportType: string): Promise<ReportResponse> =>
    api.post(`/api/v1/pipeline/dashboard/report?report_type=${reportType}`).then((res) => res.data),

  // Alerts
  getAlerts: (limit = 50): Promise<AlertsResponse> =>
    api.get(`/api/v1/pipeline/alerts/history?limit=${limit}`).then((res) => res.data),

  testAlert: (level = 'info'): Promise<ApiResponse> =>
    api.post(`/api/v1/pipeline/alerts/test?level=${level}`).then((res) => res.data),

  clearAlerts: (): Promise<ApiResponse> =>
    api.post('/api/v1/pipeline/alerts/clear-history').then((res) => res.data),
};

// Utility function to handle API errors
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'Erro desconhecido';
};

export default api;
