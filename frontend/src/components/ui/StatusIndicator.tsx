import React from 'react';
import { cn } from '../../utils/cn';

export type StatusType = 'active' | 'inactive' | 'warning';

interface StatusIndicatorProps {
  status: StatusType;
  label: string;
  className?: string;
}

const statusStyles: Record<StatusType, string> = {
  active: 'bg-success-500',
  inactive: 'bg-danger-500',
  warning: 'bg-warning-500',
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  className,
}) => {
  return (
    <div className={cn('flex items-center', className)}>
      <div className={cn('status-indicator', statusStyles[status])} />
      <span className="text-sm">{label}</span>
    </div>
  );
};
