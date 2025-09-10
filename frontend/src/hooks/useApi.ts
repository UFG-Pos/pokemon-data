import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { healthApi, pokemonApi, pipelineApi, handleApiError } from '../services/api';
import { toast } from '../utils/toast';

// Query Keys
export const queryKeys = {
  health: ['health'],
  pokemons: ['pokemons'],
  pokemonsList: (skip: number, limit: number) => ['pokemons', 'list', skip, limit],
  pipelineStatus: ['pipeline', 'status'],
  events: (limit: number) => ['pipeline', 'events', limit],
  alerts: (limit: number) => ['pipeline', 'alerts', limit],
  dashboardData: ['pipeline', 'dashboard'],
} as const;

// Health Hooks
export const useHealth = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: healthApi.getHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
  });
};

// Pokemon Hooks
export const usePokemons = (skip = 0, limit = 20) => {
  return useQuery({
    queryKey: queryKeys.pokemonsList(skip, limit),
    queryFn: () => pokemonApi.listPokemons(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useImportPokemon = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: pokemonApi.importPokemon,
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Pokémon ${data.data?.name} importado com sucesso!`);
        // Invalidate pokemon queries to refetch
        queryClient.invalidateQueries({ queryKey: queryKeys.pokemons });
        queryClient.invalidateQueries({ queryKey: queryKeys.pipelineStatus });
      } else {
        toast.error(data.message || 'Erro ao importar pokémon');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao importar pokémon: ${handleApiError(error)}`);
    },
  });
};

// Pipeline Hooks
export const usePipelineStatus = () => {
  return useQuery({
    queryKey: queryKeys.pipelineStatus,
    queryFn: pipelineApi.getStatus,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

export const useStartStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: pipelineApi.startStream,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Stream processor iniciado!');
        queryClient.invalidateQueries({ queryKey: queryKeys.pipelineStatus });
      } else {
        toast.warning(data.message || 'Erro ao iniciar stream');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao iniciar stream: ${handleApiError(error)}`);
    },
  });
};

export const useStopStream = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: pipelineApi.stopStream,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Stream processor parado!');
        queryClient.invalidateQueries({ queryKey: queryKeys.pipelineStatus });
      } else {
        toast.error('Erro ao parar stream');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao parar stream: ${handleApiError(error)}`);
    },
  });
};

export const useEvents = (limit = 10) => {
  return useQuery({
    queryKey: queryKeys.events(limit),
    queryFn: () => pipelineApi.getEvents(limit),
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useSimulateAnomaly = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ pokemonName, anomalyType }: { pokemonName: string; anomalyType: string }) =>
      pipelineApi.simulateAnomaly(pokemonName, anomalyType),
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Anomalia simulada com sucesso!');
        queryClient.invalidateQueries({ queryKey: queryKeys.events(10) });
        queryClient.invalidateQueries({ queryKey: queryKeys.alerts(10) });
      } else {
        toast.error('Erro ao simular anomalia');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao simular anomalia: ${handleApiError(error)}`);
    },
  });
};

// File Operations Hooks
export const useExportCSV = () => {
  return useMutation({
    mutationFn: pipelineApi.exportCSV,
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`CSV exportado: ${data.filepath}`);
      } else {
        toast.error('Erro ao exportar CSV');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao exportar CSV: ${handleApiError(error)}`);
    },
  });
};

export const useExportJSON = () => {
  return useMutation({
    mutationFn: pipelineApi.exportJSON,
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`JSON exportado: ${data.filepath}`);
      } else {
        toast.error('Erro ao exportar JSON');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao exportar JSON: ${handleApiError(error)}`);
    },
  });
};

export const useCleanData = () => {
  return useMutation({
    mutationFn: pipelineApi.cleanData,
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Dados limpos: ${data.result.processed} pokémons processados`);
      } else {
        toast.error('Erro na limpeza de dados');
      }
    },
    onError: (error) => {
      toast.error(`Erro na limpeza de dados: ${handleApiError(error)}`);
    },
  });
};

export const useGenerateReport = () => {
  return useMutation({
    mutationFn: pipelineApi.generateReport,
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Relatório ${data.report_type} gerado: ${data.filepath}`);
      } else {
        toast.error(`Erro ao gerar relatório`);
      }
    },
    onError: (error) => {
      toast.error(`Erro ao gerar relatório: ${handleApiError(error)}`);
    },
  });
};

// Dashboard Hooks
export const useDashboardData = () => {
  return useQuery({
    queryKey: queryKeys.dashboardData,
    queryFn: pipelineApi.getDashboardData,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

// Alerts Hooks
export const useAlerts = (limit = 10) => {
  return useQuery({
    queryKey: queryKeys.alerts(limit),
    queryFn: () => pipelineApi.getAlerts(limit),
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useTestAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: pipelineApi.testAlert,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Alerta de teste enviado!');
        queryClient.invalidateQueries({ queryKey: queryKeys.alerts(10) });
      } else {
        toast.error('Erro no teste de alerta');
      }
    },
    onError: (error) => {
      toast.error(`Erro no teste de alerta: ${handleApiError(error)}`);
    },
  });
};

export const useClearAlerts = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: pipelineApi.clearAlerts,
    onSuccess: (data) => {
      if (data.success) {
        toast.success('Histórico de alertas limpo!');
        queryClient.invalidateQueries({ queryKey: queryKeys.alerts(10) });
        queryClient.invalidateQueries({ queryKey: queryKeys.pipelineStatus });
      } else {
        toast.error('Erro ao limpar alertas');
      }
    },
    onError: (error) => {
      toast.error(`Erro ao limpar alertas: ${handleApiError(error)}`);
    },
  });
};
