// Base API Response
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// Pokemon Types
export interface PokemonType {
  name: string;
  url: string;
}

export interface PokemonAbility {
  name: string;
  url: string;
  is_hidden: boolean;
}

export interface PokemonStats {
  hp: number;
  attack: number;
  defense: number;
  'special-attack': number;
  'special-defense': number;
  speed: number;
}

export interface PokemonSprites {
  front_default: string;
  front_shiny: string;
  back_default: string;
  back_shiny: string;
}

export interface Pokemon {
  id: number;
  name: string;
  height: number;
  weight: number;
  base_experience: number;
  types: PokemonType[];
  abilities: PokemonAbility[];
  stats: PokemonStats;
  sprites: PokemonSprites;
  created_at: string;
  updated_at: string;
}

export interface PokemonListResponse extends ApiResponse {
  data: Pokemon[];
  total: number;
  skip: number;
  limit: number;
}

// Health Check
export interface HealthStatus {
  overall_status: string;
  agnos: {
    agnos_status: string;
    pokemon_mcp: string;
    mongodb_mcp: string;
  };
  database: {
    status: string;
    database: string;
    pokemon_count: number;
  };
  timestamp: string;
}

// Pipeline Status
export interface StreamProcessorStatus {
  is_running: boolean;
  processed_count: number;
  anomalies_detected: number;
  alerts_sent: number;
  last_processed: string | null;
  start_time: string | null;
}

export interface AlertSystemStatus {
  total_alerts: number;
  last_alert: string | null;
}

export interface PipelineStatus {
  stream_processor: StreamProcessorStatus;
  alert_system: AlertSystemStatus;
}

export interface PipelineStatusResponse extends ApiResponse {
  pipeline_status: PipelineStatus;
}

// Events
export interface StreamEvent {
  timestamp: string;
  pokemon_id: number;
  pokemon_name: string;
  anomalies_count: number;
  anomalies: Anomaly[];
}

export interface Anomaly {
  rule: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  details: any;
}

export interface EventsResponse extends ApiResponse {
  events: StreamEvent[];
  count: number;
}

// Alerts
export interface Alert {
  timestamp: string;
  level: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  details?: any;
}

export interface AlertsResponse extends ApiResponse {
  alerts: Alert[];
  count: number;
}

// Dashboard Data
export interface DataQuality {
  quality_score: number;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  completeness: number;
  accuracy: number;
  consistency: number;
}

export interface DashboardData {
  data_quality: DataQuality;
  pokemon_stats: {
    total_count: number;
    by_type: Record<string, number>;
    by_generation: Record<string, number>;
  };
  processing_stats: {
    total_processed: number;
    anomalies_detected: number;
    alerts_generated: number;
  };
}

export interface DashboardResponse extends ApiResponse {
  dashboard: DashboardData;
}

// File Operations
export interface FileOperationResponse extends ApiResponse {
  filepath: string;
  size?: number;
  records?: number;
}

export interface CleanDataResponse extends ApiResponse {
  result: {
    processed: number;
    cleaned: number;
    removed: number;
  };
}

// Report Generation
export interface ReportResponse extends ApiResponse {
  filepath: string;
  report_type: string;
  generated_at: string;
}
