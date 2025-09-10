import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className, onClick }) => {
  return (
    <div
      className={cn(
        'card',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
  return (
    <div className={cn('card-header', className)}>
      {children}
    </div>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className }) => {
  return (
    <div className={cn('space-y-4', className)}>
      {children}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  onClick?: () => void;
}

const colorStyles = {
  primary: 'text-primary-600',
  success: 'text-success-600',
  warning: 'text-warning-600',
  danger: 'text-danger-600',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color = 'primary',
  onClick,
}) => {
  return (
    <Card className="metric-card text-center" onClick={onClick}>
      <div className={cn('mb-2', colorStyles[color])}>
        {icon}
      </div>
      <h5 className="text-sm font-medium text-gray-600 mb-1">{title}</h5>
      <h3 className={cn('text-2xl font-bold', colorStyles[color])}>{value}</h3>
    </Card>
  );
};
