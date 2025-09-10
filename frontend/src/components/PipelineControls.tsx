import React from 'react';
import {
  Play,
  Square,
  Bug,
  FileText,
  FileCode,
  Trash2,
  Calendar,
  CalendarDays,
  BarChart3,
  Settings
} from 'lucide-react';
import { Card, CardHeader, CardContent } from './ui/Card';
import { LoadingButton } from './ui/Loading';
import { InfoTooltip, Tooltip } from './ui/Tooltip';
import { 
  useStartStream, 
  useStopStream, 
  useSimulateAnomaly,
  useExportCSV,
  useExportJSON,
  useCleanData,
  useGenerateReport
} from '../hooks/useApi';

export const PipelineControls: React.FC = () => {
  const startStreamMutation = useStartStream();
  const stopStreamMutation = useStopStream();
  const simulateAnomalyMutation = useSimulateAnomaly();
  const exportCSVMutation = useExportCSV();
  const exportJSONMutation = useExportJSON();
  const cleanDataMutation = useCleanData();
  const generateReportMutation = useGenerateReport();

  const handleSimulateAnomaly = () => {
    simulateAnomalyMutation.mutate({
      pokemonName: 'pikachu',
      anomalyType: 'negative_stats'
    });
  };

  const handleGenerateReport = (type: string) => {
    generateReportMutation.mutate(type);
  };

  const viewDashboard = () => {
    window.open('http://localhost:8000/api/v1/pipeline/dashboard/html', '_blank');
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h5 className="text-lg font-semibold flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Controles da Pipeline
          </h5>
          <InfoTooltip
            content="Controle o processamento de dados em tempo real, exporte arquivos, gere relatórios e simule anomalias para testes."
            position="left"
          />
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Stream Processing */}
        <div className="space-y-6">
          <div>
            <h6 className="font-medium mb-3 text-gray-700">Stream Processing</h6>
            <div className="flex flex-wrap gap-2">
              <LoadingButton
                isLoading={startStreamMutation.isPending}
                onClick={() => startStreamMutation.mutate()}
                className="btn-success btn-sm"
              >
                <Play className="w-4 h-4 mr-2" />
                Iniciar
              </LoadingButton>
              
              <LoadingButton
                isLoading={stopStreamMutation.isPending}
                onClick={() => stopStreamMutation.mutate()}
                className="btn-danger btn-sm"
              >
                <Square className="w-4 h-4 mr-2" />
                Parar
              </LoadingButton>
              
              <LoadingButton
                isLoading={simulateAnomalyMutation.isPending}
                onClick={handleSimulateAnomaly}
                className="btn-warning btn-sm"
              >
                <Bug className="w-4 h-4 mr-2" />
                Simular Anomalia
              </LoadingButton>
            </div>
          </div>

          {/* File Processing */}
          <div>
            <h6 className="font-medium mb-3 text-gray-700">Processamento de Arquivos</h6>
            <div className="flex flex-wrap gap-2">
              <Tooltip content="Baixa todos os pokémons em formato CSV diretamente no seu computador">
                <LoadingButton
                  isLoading={exportCSVMutation.isPending}
                  onClick={() => exportCSVMutation.mutate()}
                  className="btn-secondary btn-sm"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Exportar CSV
                </LoadingButton>
              </Tooltip>

              <Tooltip content="Baixa todos os pokémons em formato JSON diretamente no seu computador">
                <LoadingButton
                  isLoading={exportJSONMutation.isPending}
                  onClick={() => exportJSONMutation.mutate()}
                  className="btn-secondary btn-sm"
                >
                  <FileCode className="w-4 h-4 mr-2" />
                  Exportar JSON
                </LoadingButton>
              </Tooltip>

              <Tooltip content="Remove dados duplicados e inconsistentes do banco de dados">
                <LoadingButton
                  isLoading={cleanDataMutation.isPending}
                  onClick={() => cleanDataMutation.mutate()}
                  className="btn-secondary btn-sm"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Limpar Dados
                </LoadingButton>
              </Tooltip>
            </div>
          </div>

          {/* Reports */}
          <div>
            <h6 className="font-medium mb-3 text-gray-700">Relatórios</h6>
            <div className="flex flex-wrap gap-2">
              <LoadingButton
                isLoading={generateReportMutation.isPending}
                onClick={() => handleGenerateReport('daily')}
                className="btn-secondary btn-sm"
              >
                <Calendar className="w-4 h-4 mr-2" />
                Diário
              </LoadingButton>
              
              <LoadingButton
                isLoading={generateReportMutation.isPending}
                onClick={() => handleGenerateReport('weekly')}
                className="btn-secondary btn-sm"
              >
                <CalendarDays className="w-4 h-4 mr-2" />
                Semanal
              </LoadingButton>
              
              <button
                onClick={viewDashboard}
                className="btn btn-secondary btn-sm"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
