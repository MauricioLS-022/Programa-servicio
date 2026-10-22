import React from 'react';
import { ICONS, type IconName } from './iconsData';

export type { IconName };

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  name: IconName;
  size?: number | string;
  className?: string;
}

/**
 * Componente Icon nativo SVG para Material Symbols Outlined.
 * - Idéntico a la fuente de Google pero sin peticiones HTTP ni retrasos de renderizado.
 * - Soporta herencia de color nativa con `fill="currentColor"`.
 * - Totalmente accesible y tipado con TypeScript.
 */
export const Icon: React.FC<IconProps> = ({
  name,
  size = 24,
  className = '',
  style,
  ...props
}) => {
  const path = ICONS[name];

  if (!path) {
    if (import.meta.env?.DEV) {
      console.warn(`[Icon] Icono "${name}" no encontrado en iconsData.`);
    }
    return null;
  }

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 -960 960 960"
      width={size}
      height={size}
      fill="currentColor"
      className={`inline-block shrink-0 align-middle ${className}`}
      style={{
        display: 'inline-block',
        verticalAlign: 'middle',
        ...style,
      }}
      aria-hidden="true"
      {...props}
    >
      <path d={path} />
    </svg>
  );
};

export default Icon;
