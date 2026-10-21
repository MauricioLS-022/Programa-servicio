import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  icon,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer select-none';

  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-base px-6 py-2.5 gap-2.5',
  };

  const variantClasses = {
    primary:
      'bg-vino hover:bg-vino-hover text-white shadow-sm focus:ring-vino-hover dark:bg-vino-light dark:hover:bg-vino',
    secondary:
      'bg-white dark:bg-neutral-800 text-text-main dark:text-neutral-100 border border-border-subtle dark:border-neutral-700 hover:bg-surface-low dark:hover:bg-neutral-700/60 focus:ring-vino',
    danger:
      'bg-red-700 hover:bg-red-800 text-white shadow-sm focus:ring-red-600',
    ghost:
      'bg-transparent text-text-muted hover:text-text-main hover:bg-surface-low dark:hover:bg-neutral-800 focus:ring-vino',
    outline:
      'border-2 border-vino text-vino hover:bg-vino hover:text-white dark:border-vino-light dark:text-vino-light dark:hover:bg-vino-light dark:hover:text-neutral-900',
  };

  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin shrink-0" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      <span>{children}</span>
    </button>
  );
};

