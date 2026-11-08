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
      className={`bg-white dark:bg-[#1b1416] rounded-xl border border-border-subtle dark:border-[#382628] shadow-card transition-all duration-200 overflow-hidden ${className}`}
      {...props}
    >
      {(title || action || icon) && (
        <div className="px-5 py-4 border-b border-border-subtle/60 dark:border-[#382628] flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="p-2 rounded-lg bg-surface-container dark:bg-[#2f2225] text-vino dark:text-[#ffdad6] shrink-0">
                {icon}
              </div>
            )}
            <div>
              {title && (
                <h3 className="font-serif text-base font-bold text-text-main dark:text-[#f8f2f0] tracking-tight">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-xs text-text-muted dark:text-[#d4c2bf] mt-0.5">{subtitle}</p>
              )}
            </div>
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className="p-5">{children}</div>
      {footer && (
        <div className="px-5 py-3.5 bg-surface-low/50 dark:bg-[#181213] border-t border-border-subtle/60 dark:border-[#382628]">
          {footer}
        </div>
      )}
    </div>
  );
};
