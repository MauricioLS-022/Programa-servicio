import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  headerIcon?: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'md',
  headerIcon,
}) => {
  const [isMounted, setIsMounted] = useState(isOpen);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    if (isOpen) {
      setIsMounted(true);
      timer = setTimeout(() => setIsAnimating(true), 20);
    } else {
      setIsAnimating(false);
      timer = setTimeout(() => setIsMounted(false), 250);
    }
    return () => clearTimeout(timer);
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isMounted) return null;

  const maxWidthClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg sm:max-w-xl',
    lg: 'max-w-xl sm:max-w-2xl lg:max-w-3xl',
    xl: 'max-w-2xl sm:max-w-3xl lg:max-w-4xl',
    '2xl': 'max-w-3xl sm:max-w-4xl lg:max-w-5xl',
  };

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center p-3 sm:p-5 overflow-hidden">
      {/* Backdrop con desenfoque y animación de opacidad */}
      <div
        className={`fixed inset-0 bg-[#120a0b]/70 dark:bg-black/80 backdrop-blur-sm transition-opacity duration-250 ease-out ${
          isAnimating ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog contenido con scroll interno independiente */}
      <div
        className={`relative w-full ${maxWidthClasses[maxWidth]} max-h-[90vh] sm:max-h-[92vh] flex flex-col bg-white dark:bg-[#1b1416] rounded-2xl shadow-2xl border border-border-subtle/80 dark:border-[rgba(221,192,189,0.2)] overflow-hidden transform transition-all duration-250 ease-out ${
          isAnimating ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-3'
        }`}
        role="dialog"
        aria-modal="true"
      >
        {/* Cabecera canónica Jinja2 (Degradado vino institucional) */}
        {title && (
          <div className="modal-header px-6 py-4 sm:px-7 sm:py-4.5 bg-gradient-to-r from-[#700204] to-[#390002] dark:from-[#38070a] dark:to-[#1c0305] text-white flex items-center justify-between border-b border-white/10 shrink-0 select-none">
            <div className="modal-title-group flex items-center gap-3 min-w-0 pr-3">
              {headerIcon && (
                <span className="modal-icon text-white/90 shrink-0 flex items-center justify-center">
                  {headerIcon}
                </span>
              )}
              <div className="min-w-0">
                <h3 className="modal-title font-serif text-lg sm:text-xl font-bold tracking-tight text-white m-0 truncate">
                  {title}
                </h3>
                {description && (
                  <p className="text-xs text-white/80 m-0 mt-0.5 truncate font-normal">
                    {description}
                  </p>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="modal-close w-8 h-8 rounded-full bg-white/15 hover:bg-white/30 active:bg-white/40 text-white flex items-center justify-center transition-all cursor-pointer border-none shrink-0"
              aria-label="Cerrar modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Cuerpo del Modal con scroll acotado y contención de rebote */}
        <div
          className="flex-1 min-h-0 overflow-y-auto custom-scrollbar px-6 py-5 sm:px-8 sm:py-6 text-text-main dark:text-neutral-100"
          style={{ overscrollBehavior: 'contain' }}
        >
          {children}
        </div>

        {/* Footer del Modal fijado en la parte inferior */}
        {footer && (
          <div className="flex-shrink-0 px-6 py-4 sm:px-8 sm:py-4.5 bg-surface-low/50 dark:bg-[#1f1618] border-t border-border-subtle/80 dark:border-[rgba(221,192,189,0.18)] flex items-center justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
