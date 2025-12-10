import { z } from 'zod';

// Vehicle schema
export const VehicleSchema = z.object({
  id: z.number(),
  vehicle_id: z.string(),
  route_id: z.string().nullable(),
  route_name: z.string().nullable(),
  latitude: z.number().nullable(),
  longitude: z.number().nullable(),
  bearing: z.number().nullable(),
  speed: z.number().nullable(),
  current_status: z.string().nullable(),
  last_updated: z.string(),
});

// Health status schema
export const HealthStatusSchema = z.object({
  status: z.string(),
  database: z.string(),
  last_collection: z.string().nullable(),
  uptime_seconds: z.number(),
  vehicles_tracked: z.number(),
  message: z.string().optional(),
});

// System analytics schema
export const SystemAnalyticsSchema = z.object({
  total_telemetry_events: z.number(),
  routes_monitored: z.number(),
  vehicles_tracked: z.number(),
  events_last_hour: z.number(),
  events_per_second: z.number(),
  collection_frequency_seconds: z.number(),
});

// Route delay schema
export const RouteDelaySchema = z.object({
  hour_of_day: z.number(),
  avg_delay_minutes: z.number(),
  sample_count: z.number(),
  calculated_at: z.string(),
});

// Type exports
export type Vehicle = z.infer<typeof VehicleSchema>;
export type HealthStatus = z.infer<typeof HealthStatusSchema>;
export type SystemAnalytics = z.infer<typeof SystemAnalyticsSchema>;
export type RouteDelay = z.infer<typeof RouteDelaySchema>;
