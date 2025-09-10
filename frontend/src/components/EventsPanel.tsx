import React from 'react';
import { RefreshCw, Clock, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardContent } from './ui/Card';
import { Loading } from './ui/Loading';
import { InfoTooltip } from './ui/Tooltip';
import { useEvents } from '../hooks/useApi';
import type { StreamEvent } from '../types/api';

interface EventItemProps {
  event: StreamEvent;
}

const EventItem: React.FC<EventItemProps> = ({ event }) => {
  const time = new Date(event.timestamp).toLocaleTimeString();
  
  return (
    <div className="flex items-start space-x-3 py-2 border-b border-gray-100 last:border-b-0">
      <div className="flex-shrink-0">
        <Clock className="w-4 h-4 text-gray-400 mt-0.5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gray-900 capitalize">
            {event.pokemon_name}
          </p>
          <span className="text-xs text-gray-500">{time}</span>
        </div>
        {event.anomalies_count > 0 && (
          <div className="mt-1">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-warning-100 text-warning-800">
              <AlertTriangle className="w-3 h-3 mr-1" />
              {event.anomalies_count} anomalias
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export const EventsPanel: React.FC = () => {
  const { data: eventsData, isLoading, refetch, isFetching } = useEvents(10);

  const handleRefresh = () => {
    refetch();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <h5 className="text-lg font-semibold flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Eventos Recentes
            </h5>
            <InfoTooltip
              content="Visualize eventos de processamento em tempo real, incluindo pokémons processados e anomalias detectadas."
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
        <div className="log-container">
          {isLoading ? (
            <Loading text="Carregando eventos..." />
          ) : eventsData?.events && eventsData.events.length > 0 ? (
            <div className="space-y-1">
              {eventsData.events.map((event, index) => (
                <EventItem key={`${event.pokemon_id}-${event.timestamp}-${index}`} event={event} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p>Nenhum evento recente</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
