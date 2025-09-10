import React from 'react';
import { Database, Activity, AlertTriangle, BarChart3 } from 'lucide-react';
import { MetricCard } from './ui/Card';
import { StatusIndicator } from './ui/StatusIndicator';
import { Loading } from './ui/Loading';
import { PokemonManagement } from './PokemonManagement';
import { PipelineControls } from './PipelineControls';
import { EventsPanel } from './EventsPanel';
import { AlertsPanel } from './AlertsPanel';
import { useHealth, usePipelineStatus, useDashboardData, usePokemons } from '../hooks/useApi';

export const Dashboard: React.FC = () => {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: pipelineStatus, isLoading: pipelineLoading } = usePipelineStatus();
  const { data: dashboardData, isLoading: dashboardLoading } = useDashboardData();
  const { data: pokemonsData, isLoading: pokemonsLoading } = usePokemons(0, 1);

  const isLoading = healthLoading || pipelineLoading || dashboardLoading || pokemonsLoading;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" text="Carregando dashboard..." />
      </div>
    );
  }

  const totalPokemons = pokemonsData?.total || 0;
  const streamStatus = pipelineStatus?.pipeline_status?.stream_processor?.is_running ? 'active' : 'inactive';
  const totalAlerts = pipelineStatus?.pipeline_status?.alert_system?.total_alerts || 0;
  const dataQuality = dashboardData?.dashboard?.data_quality?.quality_score || 0;
  const connectionStatus = health?.overall_status === 'healthy' ? 'active' : 'inactive';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-primary-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 mr-3" />
              <h1 className="text-xl font-bold">Pokemon Pipeline Dashboard</h1>
            </div>
            <StatusIndicator
              status={connectionStatus}
              label={connectionStatus === 'active' ? 'Conectado' : 'Desconectado'}
              className="text-white"
            />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Pokémons"
            value={totalPokemons}
            icon={<Database className="w-8 h-8 mx-auto" />}
            color="primary"
          />
          
          <div className="card text-center">
            <div className="text-success-600 mb-2">
              <Activity className="w-8 h-8 mx-auto" />
            </div>
            <h5 className="text-sm font-medium text-gray-600 mb-1">Stream Processor</h5>
            <StatusIndicator
              status={streamStatus}
              label={streamStatus === 'active' ? 'Ativo' : 'Inativo'}
              className="justify-center"
            />
          </div>

          <MetricCard
            title="Alertas"
            value={totalAlerts}
            icon={<AlertTriangle className="w-8 h-8 mx-auto" />}
            color="warning"
          />

          <MetricCard
            title="Qualidade"
            value={`${dataQuality.toFixed(1)}%`}
            icon={<BarChart3 className="w-8 h-8 mx-auto" />}
            color="success"
          />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Pokemon Management */}
          <PokemonManagement />

          {/* Pipeline Controls */}
          <PipelineControls />

          {/* Events */}
          <EventsPanel />

          {/* Alerts */}
          <AlertsPanel />
        </div>
      </div>
    </div>
  );
};
