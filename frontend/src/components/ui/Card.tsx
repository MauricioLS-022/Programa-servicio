import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  icon,
  footer,
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`bg-white dark:bg-neutral-800/90 rounded-xl border border-border-subtle dark:border-neutral-700/80 shadow-card transition-all duration-200 overflow-hidden ${className}`}
      {...props}
    >
      {(title || action || icon) && (
        <div className="px-5 py-4 border-b border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="p-2 rounded-lg bg-surface-container dark:bg-neutral-700/50 text-vino dark:text-vino-light shrink-0">
                {icon}
              </div>
            )}
            <div>
              {title && (
                <h3 className="font-serif text-base font-bold text-text-main dark:text-neutral-100 tracking-tight">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-xs text-text-muted dark:text-neutral-400 mt-0.5">{subtitle}</p>
              )}
            </div>
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className="p-5">{children}</div>
      {footer && (
        <div className="px-5 py-3.5 bg-surface-low/50 dark:bg-neutral-800/40 border-t border-border-subtle/60 dark:border-neutral-700/60">
          {footer}
        </div>
      )}
    </div>
  );
};

