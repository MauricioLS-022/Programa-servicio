import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
  description?: string;
}

interface ToastContextValue {
  showToast: (type: ToastType, message: string, description?: string) => void;
  success: (message: string, description?: string) => void;
  error: (message: string, description?: string) => void;
  warning: (message: string, description?: string) => void;
  info: (message: string, description?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    (type: ToastType, message: string, description?: string) => {
      const id = `${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
      setToasts((prev) => [...prev, { id, type, message, description }]);

      setTimeout(() => {
        removeToast(id);
      }, 4500);
    },
    [removeToast]
  );

  const success = useCallback(
    (msg: string, desc?: string) => showToast('success', msg, desc),
    [showToast]
  );
  const error = useCallback(
    (msg: string, desc?: string) => showToast('error', msg, desc),
    [showToast]
  );
  const warning = useCallback(
    (msg: string, desc?: string) => showToast('warning', msg, desc),
    [showToast]
  );
  const info = useCallback(
    (msg: string, desc?: string) => showToast('info', msg, desc),
    [showToast]
  );

  return (
    <ToastContext.Provider value={{ showToast, success, error, warning, info }}>
      {children}
      {/* Toast Container */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((toast) => {
          const typeConfig = {
            success: {
              icon: <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />,
              border: 'border-emerald-200 dark:border-emerald-900',
              bg: 'bg-white dark:bg-neutral-800',
            },
            error: {
              icon: <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0" />,
              border: 'border-red-200 dark:border-red-900',
              bg: 'bg-white dark:bg-neutral-800',
            },
            warning: {
              icon: <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />,
              border: 'border-amber-200 dark:border-amber-900',
              bg: 'bg-white dark:bg-neutral-800',
            },
            info: {
              icon: <Info className="w-5 h-5 text-vino dark:text-vino-light shrink-0" />,
              border: 'border-border-subtle dark:border-neutral-700',
              bg: 'bg-white dark:bg-neutral-800',
            },
          }[toast.type];

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto p-4 rounded-xl border ${typeConfig.border} ${typeConfig.bg} shadow-lg flex items-start gap-3 transition-all duration-300 transform animate-in slide-in-from-bottom-5`}
            >
              {typeConfig.icon}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-text-main dark:text-neutral-100">
                  {toast.message}
                </p>
                {toast.description && (
                  <p className="text-xs text-text-muted dark:text-neutral-400 mt-0.5">
                    {toast.description}
                  </p>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-text-muted hover:text-text-main dark:text-neutral-400 dark:hover:text-neutral-200 p-0.5 rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

