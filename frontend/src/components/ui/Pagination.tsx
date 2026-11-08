import React, { useMemo } from 'react';
import { Icon } from './Icon';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems?: number;
  itemsPerPage?: number;
  onPageChange: (page: number) => void;
  itemLabel?: string;
  className?: string;
}

/**
 * Componente Pagination Institucional Vino Nuevo.
 * - Diseño minimalista elegante alineado a la paleta institucional (Modo Claro y Oscuro).
 * - Se renderiza siempre (evitando desaparición del layout en 1 sola página).
 * - Botones táctiles optimizados con feedback visual y soporte de accesibilidad completo (Aria).
 */
export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage = 5,
  onPageChange,
  itemLabel = 'registros',
  className = '',
}) => {
  const safeTotalPages = Math.max(1, totalPages || 1);
  const safeCurrentPage = Math.min(Math.max(1, currentPage || 1), safeTotalPages);

  // Rango deslizante de páginas (ventana de hasta 5 páginas visibles)
  const paginationRange = useMemo(() => {
    const delta = 2;
    const range: number[] = [];
    const left = Math.max(1, safeCurrentPage - delta);
    const right = Math.min(safeTotalPages, safeCurrentPage + delta);

    for (let i = left; i <= right; i++) {
      range.push(i);
    }
    return range;
  }, [safeCurrentPage, safeTotalPages]);

  // Cálculos de elementos visibles
  const startItem = totalItems !== undefined && totalItems > 0 ? (safeCurrentPage - 1) * itemsPerPage + 1 : 0;
  const endItem =
    totalItems !== undefined
      ? Math.min(safeCurrentPage * itemsPerPage, totalItems)
      : safeCurrentPage * itemsPerPage;

  return (
    <div className={`pagination-footer ${className}`} role="navigation" aria-label="Paginación de resultados">
      <div className="pagination-info">
        {totalItems !== undefined ? (
          totalItems > 0 ? (
            <span>
              Mostrando <strong>{startItem}</strong> - <strong>{endItem}</strong> de <strong>{totalItems}</strong> {itemLabel}
              {safeTotalPages > 1 && ` (Página ${safeCurrentPage} de ${safeTotalPages})`}
            </span>
          ) : (
            <span>0 {itemLabel} encontrados</span>
          )
        ) : (
          <span>
            Página <strong>{safeCurrentPage}</strong> de <strong>{safeTotalPages}</strong>
          </span>
        )}
      </div>

      <div className="pagination-controls">
        {/* Botón Anterior */}
        <button
          type="button"
          className="pagination-btn"
          onClick={() => onPageChange(Math.max(1, safeCurrentPage - 1))}
          disabled={safeCurrentPage <= 1}
          aria-label="Página anterior"
          title="Página anterior"
        >
          <Icon name="chevron_left" size={18} />
        </button>

        {/* Primera página si la ventana no la incluye */}
        {paginationRange[0] > 1 && (
          <>
            <button
              type="button"
              className={`pagination-btn ${safeCurrentPage === 1 ? 'active' : ''}`}
              onClick={() => onPageChange(1)}
              aria-label="Página 1"
              aria-current={safeCurrentPage === 1 ? 'page' : undefined}
            >
              1
            </button>
            {paginationRange[0] > 2 && (
              <span className="px-1 text-xs text-text-muted dark:text-neutral-500 select-none" aria-hidden="true">
                ...
              </span>
            )}
          </>
        )}

        {/* Páginas en la ventana deslizante */}
        {paginationRange.map((pageNumber) => (
          <button
            key={pageNumber}
            type="button"
            className={`pagination-btn ${pageNumber === safeCurrentPage ? 'active' : ''}`}
            onClick={() => onPageChange(pageNumber)}
            aria-label={`Página ${pageNumber}`}
            aria-current={pageNumber === safeCurrentPage ? 'page' : undefined}
          >
            {pageNumber}
          </button>
        ))}

        {/* Última página si la ventana no la incluye */}
        {paginationRange[paginationRange.length - 1] < safeTotalPages && (
          <>
            {paginationRange[paginationRange.length - 1] < safeTotalPages - 1 && (
              <span className="px-1 text-xs text-text-muted dark:text-neutral-500 select-none" aria-hidden="true">
                ...
              </span>
            )}
            <button
              type="button"
              className={`pagination-btn ${safeCurrentPage === safeTotalPages ? 'active' : ''}`}
              onClick={() => onPageChange(safeTotalPages)}
              aria-label={`Página ${safeTotalPages}`}
              aria-current={safeCurrentPage === safeTotalPages ? 'page' : undefined}
            >
              {safeTotalPages}
            </button>
          </>
        )}

        {/* Botón Siguiente */}
        <button
          type="button"
          className="pagination-btn"
          onClick={() => onPageChange(Math.min(safeTotalPages, safeCurrentPage + 1))}
          disabled={safeCurrentPage >= safeTotalPages}
          aria-label="Página siguiente"
          title="Página siguiente"
        >
          <Icon name="chevron_right" size={18} />
        </button>
      </div>
    </div>
  );
};
