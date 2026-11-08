import React from 'react';
import { Icon } from '../ui/Icon';

interface PageLoadingFallbackProps {
  message?: string;
  minHeight?: string;
}

/**
 * Componente de carga institucional para transiciones de rutas y Suspense diferido.
 * - Totalmente accesible con roles ARIA de anuncio en vivo.
 * - Mantiene los colores institucionales (borgoña/vino) con animación suave.
 */
export const PageLoadingFallback: React.FC<PageLoadingFallbackProps> = ({
  message = 'Cargando contenido...',
  minHeight = 'min-h-[60vh]',
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className={`w-full ${minHeight} flex flex-col items-center justify-center p-6 text-center select-none`}
    >
      <div className="relative flex items-center justify-center mb-4">
        {/* Anillo de pulso sutil de fondo */}
        <div className="absolute w-12 h-12 rounded-full bg-[#4A0203]/10 dark:bg-[#ffdad6]/10 animate-ping" />
        {/* Spinner institucional de alta resolución */}
        <Icon
          name="progress_activity"
          size={36}
          className="text-[#4A0203] dark:text-[#ffdad6] animate-spin"
        />
      </div>
      <p className="text-sm font-medium text-[#4A0203] dark:text-[#ffdad6] tracking-wide animate-pulse">
        {message}
      </p>
      <span className="sr-only">Por favor espere mientras se cargan los recursos de la vista.</span>
    </div>
  );
};

export default PageLoadingFallback;
