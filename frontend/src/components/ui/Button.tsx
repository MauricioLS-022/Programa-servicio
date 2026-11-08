import React from 'react';
import { Icon } from './Icon';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'danger-outline' | 'danger-ghost' | 'ghost' | 'outline';
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
      'bg-vino hover:bg-vino-hover text-white shadow-sm focus:ring-vino-hover dark:bg-[#8b1518] dark:hover:bg-[#a82e2e]',
    secondary:
      'bg-white dark:bg-[#1b1416] text-text-main dark:text-[#f8f2f0] border border-border-subtle dark:border-[#382628] hover:bg-surface-low dark:hover:bg-[#2f2225] focus:ring-vino',
    danger:
      'bg-red-700 hover:bg-red-800 text-white shadow-sm focus:ring-red-600 dark:bg-red-700 dark:hover:bg-red-800',
    'danger-outline':
      'border border-red-500/40 text-red-600 hover:bg-red-50 hover:border-red-600 dark:border-red-500/40 dark:text-red-400 dark:hover:bg-red-950/40 focus:ring-red-500',
    'danger-ghost':
      'bg-transparent text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40 focus:ring-red-500',
    ghost:
      'bg-transparent text-text-muted hover:text-text-main hover:bg-surface-low dark:hover:bg-[#1f1618] focus:ring-vino',
    outline:
      'border-2 border-vino text-vino hover:bg-vino hover:text-white dark:border-[#ffdad6] dark:text-[#ffdad6] dark:hover:bg-[#8b1518] dark:hover:text-white',
  };

  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Icon name="progress_activity" size={16} className="icon-spin shrink-0" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      <span>{children}</span>
    </button>
  );
};
