import React from 'react';
import { RefreshCw, Bell, Trash2, TestTube, AlertTriangle, Info, XCircle } from 'lucide-react';
import { Card, CardHeader, CardContent } from './ui/Card';
import { Loading, LoadingButton } from './ui/Loading';
import { InfoTooltip } from './ui/Tooltip';
import { useAlerts, useTestAlert, useClearAlerts } from '../hooks/useApi';
import type { Alert } from '../types/api';

interface AlertItemProps {
  alert: Alert;
}

const AlertItem: React.FC<AlertItemProps> = ({ alert }) => {
  const time = new Date(alert.timestamp).toLocaleTimeString();
  
  const levelIcons = {
    info: <Info className="w-4 h-4" />,
    warning: <AlertTriangle className="w-4 h-4" />,
    critical: <XCircle className="w-4 h-4" />,
  };

  const levelStyles = {
    info: 'text-blue-600 bg-blue-50 border-blue-200',
    warning: 'text-warning-600 bg-warning-50 border-warning-200',
    critical: 'text-danger-600 bg-danger-50 border-danger-200',
  };

  return (
    <div className="flex items-start space-x-3 py-3 border-b border-gray-100 last:border-b-0">
      <div className={`flex-shrink-0 p-1 rounded-full ${levelStyles[alert.level]}`}>
        {levelIcons[alert.level]}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${levelStyles[alert.level]}`}>
            {alert.level}
          </span>
          <span className="text-xs text-gray-500">{time}</span>
        </div>
        <p className="mt-1 text-sm font-medium text-gray-900">{alert.title}</p>
        {alert.message && (
          <p className="mt-1 text-sm text-gray-600">{alert.message}</p>
        )}
      </div>
    </div>
  );
};

export const AlertsPanel: React.FC = () => {
  const { data: alertsData, isLoading, refetch, isFetching } = useAlerts(10);
  const testAlertMutation = useTestAlert();
  const clearAlertsMutation = useClearAlerts();

  const handleRefresh = () => {
    refetch();
  };

  const handleTestAlert = () => {
    testAlertMutation.mutate('info');
  };

  const handleClearAlerts = () => {
    if (window.confirm('Tem certeza que deseja limpar o histórico de alertas?')) {
      clearAlertsMutation.mutate();
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <h5 className="text-lg font-semibold flex items-center">
              <Bell className="w-5 h-5 mr-2" />
              Alertas
            </h5>
            <InfoTooltip
              content="Sistema de alertas para monitoramento de anomalias e eventos críticos. Teste e gerencie notificações."
              position="top"
              className="ml-2"
            />
          </div>
          <button
            onClick={handleRefresh}
            disabled={isFetching}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2 mb-4">
          <LoadingButton
            isLoading={testAlertMutation.isPending}
            onClick={handleTestAlert}
            className="btn-warning btn-sm"
          >
            <TestTube className="w-4 h-4 mr-2" />
            Teste
          </LoadingButton>
          
          <LoadingButton
            isLoading={clearAlertsMutation.isPending}
            onClick={handleClearAlerts}
            className="btn-danger btn-sm"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Limpar
          </LoadingButton>
        </div>

        {/* Alerts List */}
        <div className="log-container">
          {isLoading ? (
            <Loading text="Carregando alertas..." />
          ) : alertsData?.alerts && alertsData.alerts.length > 0 ? (
            <div className="space-y-1">
              {alertsData.alerts.map((alert, index) => (
                <AlertItem key={`${alert.timestamp}-${index}`} alert={alert} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p>Nenhum alerta recente</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
