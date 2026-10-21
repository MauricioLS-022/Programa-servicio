import React, { useState } from 'react';
import { useReportes } from '../hooks/useReportes';
import { useToast } from '../context/ToastContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import {
  Search,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Reporte } from '../types/reporte';

export const ReportesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [fechaDesde, setFechaDesde] = useState('');
  const [fechaHasta, setFechaHasta] = useState('');
  const [page, setPage] = useState(1);

  // Modal State for Delete
  const [reporteToDelete, setReporteToDelete] = useState<Reporte | null>(null);

  const {
    reportes,
    total,
    pages,
    isLoading,
    eliminarReporte,
    isEliminando,
  } = useReportes({
    q: search,
    fecha_desde: fechaDesde,
    fecha_hasta: fechaHasta,
    page,
    per_page: 10,
  });

  const { success, error } = useToast();

  const handleConfirmDelete = async () => {
    if (!reporteToDelete) return;
    try {
      await eliminarReporte({
        id: reporteToDelete.id,
        cdp_id: reporteToDelete.cdp_id,
      });
      success('Reporte eliminado correctamente');
      setReporteToDelete(null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        error(err.message || 'Error al eliminar el reporte');
      } else {
        error('Error al eliminar el reporte');
      }
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-text-main dark:text-neutral-100 tracking-tight">
            Historial de Reportes
          </h1>
          <p className="text-xs sm:text-sm text-text-muted dark:text-neutral-400 mt-1">
            Auditoría de reuniones y ofrendas ({total} reportes registrados)
          </p>
        </div>

        <Link to="/generar-reporte">
          <Button variant="primary" icon={<Plus className="w-4 h-4" />}>
            Cargar Nuevo Reporte
          </Button>
        </Link>
      </div>

      {/* Filter Bar */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Input
            placeholder="Buscar por tema, líder o código..."
            icon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />

          <Input
            type="date"
            placeholder="Desde"
            value={fechaDesde}
            onChange={(e) => {
              setFechaDesde(e.target.value);
              setPage(1);
            }}
          />

          <Input
            type="date"
            placeholder="Hasta"
            value={fechaHasta}
            onChange={(e) => {
              setFechaHasta(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </Card>

      {/* Table / List */}
      <Card className="p-0 overflow-hidden">
        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
            <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
              Consultando reportes...
            </p>
          </div>
        ) : reportes.length === 0 ? (
          <div className="py-16 text-center text-text-muted dark:text-neutral-400 text-sm">
            No se encontraron reportes con los filtros seleccionados.
          </div>
        ) : (
          <div className="overflow-x-auto scroll-containment">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-low dark:bg-neutral-800/80 border-b border-border-subtle/80 dark:border-neutral-700/80 text-text-muted dark:text-neutral-400 font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Fecha</th>
                  <th className="py-3 px-4">Casa / Red</th>
                  <th className="py-3 px-4">Tema</th>
                  <th className="py-3 px-4 text-center">Asistentes</th>
                  <th className="py-3 px-4 text-right">Ofrenda USD</th>
                  <th className="py-3 px-4 text-right">Ofrenda Bs</th>
                  <th className="py-3 px-4 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle/50 dark:divide-neutral-700/50">
                {reportes.map((rep) => (
                  <tr
                    key={rep.id}
                    className="hover:bg-surface-low/50 dark:hover:bg-neutral-800/40 transition-colors"
                  >
                    <td className="py-3.5 px-4 font-semibold text-text-main dark:text-neutral-200 whitespace-nowrap">
                      {rep.fecha}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-text-main dark:text-neutral-200">
                        {rep.cdp_codigo || `CDP #${rep.cdp_id}`}
                      </span>
                      {rep.red_nombre && (
                        <span className="block text-[11px] text-text-muted dark:text-neutral-400">
                          {rep.red_nombre}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-text-muted dark:text-neutral-300 max-w-xs truncate">
                      {rep.tema || 'Sin tema especificado'}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-vino/10 text-vino dark:bg-vino/20 dark:text-vino-light">
                        {rep.asistencia}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-bold text-emerald-700 dark:text-emerald-400">
                      ${Number(rep.total_usd ?? (rep.ofrenda_efectivo_usd || 0)).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-medium text-text-muted dark:text-neutral-300">
                      Bs {Number(rep.total_bs ?? (rep.ofrenda_efectivo_bs || 0)).toLocaleString('es-VE', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => setReporteToDelete(rep)}
                        className="p-1.5 rounded-lg text-text-muted hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 cursor-pointer transition-colors"
                        title="Eliminar Reporte"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Sliding Window Pagination (±2) */}
        {pages > 1 && (
          <div className="px-5 py-4 border-t border-border-subtle/80 dark:border-neutral-700/80 flex items-center justify-between">
            <span className="text-xs text-text-muted dark:text-neutral-400">
              Página {page} de {pages} ({total} registros)
            </span>
            <div className="flex items-center gap-1.5">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= pages}
                onClick={() => setPage((p) => Math.min(p + 1, pages))}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Confirmation Modal */}
      <Modal
        isOpen={Boolean(reporteToDelete)}
        onClose={() => setReporteToDelete(null)}
        title="Confirmar Eliminación"
        maxWidth="sm"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setReporteToDelete(null)}
              disabled={isEliminando}
            >
              Cancelar
            </Button>
            <Button
              variant="danger"
              isLoading={isEliminando}
              onClick={handleConfirmDelete}
            >
              Sí, Eliminar
            </Button>
          </>
        }
      >
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-full bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-text-main dark:text-neutral-100">
              ¿Estás seguro de que deseas eliminar este reporte?
            </p>
            <p className="text-xs text-text-muted dark:text-neutral-400 mt-1">
              Esta acción no se puede deshacer. Se actualizarán las métricas ministeriales
              del Dashboard.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};
