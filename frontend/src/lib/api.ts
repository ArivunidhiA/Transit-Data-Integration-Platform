import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for faster responses
});

// Retry logic helper
async function withRetry<T>(
  fn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && axios.isAxiosError(error)) {
      const status = error.response?.status;
      // Retry on network errors or 5xx errors
      if (!status || (status >= 500 && status < 600)) {
        await new Promise(resolve => setTimeout(resolve, delay));
        return withRetry(fn, retries - 1, delay * 2); // Exponential backoff
      }
    }
    throw error;
  }
}

export interface Vehicle {
  id: number;
  vehicle_id: string;
  route_id: string | null;
  route_name: string | null;
  latitude: number | null;
  longitude: number | null;
  bearing: number | null;
  speed: number | null;
  current_status: string | null;
  last_updated: string;
}

export interface SystemAnalytics {
  total_telemetry_events: number;
  routes_monitored: number;
  vehicles_tracked: number;
  events_last_hour: number;
  events_per_second: number;
  collection_frequency_seconds: number;
}

export interface HealthStatus {
  status: string;
  database: string;
  last_collection: string | null;
  uptime_seconds: number;
  vehicles_tracked: number;
  message?: string;
}

export interface RouteDelay {
  hour_of_day: number;
  avg_delay_minutes: number;
  sample_count: number;
  calculated_at: string;
}

export interface HeadwayAnalysis {
  route_id: string | null;
  analysis: Record<string, {
    count: number;
    avg_minutes: number;
    min_minutes: number;
    max_minutes: number;
    headways: number[];
  }>;
}

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: AxiosError
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export const apiClient = {
  // Health check
  getHealth: async (): Promise<HealthStatus> => {
    try {
      const response = await withRetry(() => api.get('/health'));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch health status: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // Vehicles
  getVehicles: async (routeId?: string): Promise<Vehicle[]> => {
    try {
      const params = routeId ? { route_id: routeId } : {};
      const response = await withRetry(() => api.get('/vehicles', { params }));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch vehicles: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // System analytics
  getSystemAnalytics: async (): Promise<SystemAnalytics> => {
    try {
      const response = await withRetry(() => api.get('/analytics/system'));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch system analytics: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // Route delays
  getRouteDelays: async (routeId: string, hours: number = 24): Promise<{ route_id: string; hours_back: number; delays: RouteDelay[] }> => {
    try {
      const response = await withRetry(() => api.get(`/routes/${routeId}/delays`, { params: { hours } }));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch route delays: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // Headway analysis
  getHeadwayAnalysis: async (routeId?: string): Promise<HeadwayAnalysis> => {
    try {
      const params = routeId ? { route_id: routeId } : {};
      const response = await withRetry(() => api.get('/analytics/headway', { params }));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch headway analysis: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // Metrics
  getMetrics: async (): Promise<any> => {
    try {
      const response = await withRetry(() => api.get('/metrics'));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch metrics: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },

  // Alerts
  getAlerts: async (routeId?: string): Promise<any> => {
    try {
      const params = routeId ? { route_id: routeId } : {};
      const response = await withRetry(() => api.get('/alerts', { params }));
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          `Failed to fetch alerts: ${error.response?.statusText || 'Network error'}`,
          error.response?.status,
          error
        );
      }
      throw error;
    }
  },
};

export default apiClient;