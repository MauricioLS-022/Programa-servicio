import React from 'react';
import { Modal } from '../../ui/Modal';
import { Icon } from '../../ui/Icon';
import { Input } from '../../ui/Input';
import type { LiderReporteItem } from '../../../types/liderDashboard';

export interface LiderDetalleModalProps {
  isOpen: boolean;
  onClose: () => void;
  reporte: LiderReporteItem | null;
}

const formatMoneda = (val?: number) => {
  return Number(val || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const formatTime12h = (timeStr?: string) => {
  if (!timeStr) return 'No registrado';
  const match = timeStr.trim().match(/^(\d{1,2}):(\d{2})/);
  if (!match) return timeStr;
  let hours = parseInt(match[1], 10);
  const minutes = match[2];
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  const padHours = hours < 10 ? '0' + hours : hours;
  return `${padHours}:${minutes} ${ampm}`;
};

export const LiderDetalleModal: React.FC<LiderDetalleModalProps> = ({
  isOpen,
  onClose,
  reporte,
}) => {
  if (!reporte) return null;

  const tieneCesta =
    reporte.cesta_amor === true ||
    reporte.cesta_amor === 1 ||
    reporte.cesta_amor === '1' ||
    String(reporte.cesta_amor || '').trim().toLowerCase() === 'sí' ||
    String(reporte.cesta_amor || '').trim().toLowerCase() === 'si';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalle de la Reunión"
      headerIcon={
        <div className="modal-header-icon">
          <Icon name="visibility" size={20} />
        </div>
      }
      maxWidth="lg"
      footer={
        <div className="flex items-center justify-end w-full">
          <button
            type="button"
            className="btn-modal btn-modal-cancel"
            onClick={onClose}
            data-testid="btn-cerrar-detalle"
          >
            Cerrar
          </button>
        </div>
      }
    >
      <div className="flex flex-col gap-2.5 py-0.5" data-testid="lider-modal-detalle-body">
        {/* Sección 1: Datos de la Reunión */}
        <div className="modal-section-card">
          <h4 className="modal-section-title">
            <Icon name="calendar_today" size={16} />
            <span>Fecha y Encargado</span>
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-2.5">
            <Input
              label="Líder Encargado"
              type="text"
              readOnly
              value={reporte.lider_nombre || '—'}
            />
            <Input
              label="Fecha de Reunión"
              type="text"
              readOnly
              value={reporte.fecha_formateada || reporte.fecha || '—'}
            />
            <Input
              label="Horario de Servicio"
              type="text"
              readOnly
              value={
                reporte.hr_inicio && reporte.hr_fin
                  ? `${formatTime12h(reporte.hr_inicio)} – ${formatTime12h(reporte.hr_fin)}`
                  : reporte.hr_inicio
                  ? formatTime12h(reporte.hr_inicio)
                  : 'No registrado'
              }
            />
          </div>

          <Input
            label="Tema Desarrollado"
            type="text"
            readOnly
            value={reporte.tema || '—'}
          />
        </div>

        {/* Fila en 2 Columnas para Asistencia y Frutos */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {/* Columna Izquierda: Asistencia y Desglose */}
          <div className="modal-section-card flex flex-col justify-between">
            <div>
              <h4 className="modal-section-title">
                <Icon name="groups" size={16} />
                <span>Asistencia y Desglose</span>
              </h4>

              <div className="grid grid-cols-2 gap-2 mb-2">
                <Input
                  label="Regulares"
                  type="text"
                  readOnly
                  value={String(reporte.nro_regulares || 0)}
                  className="text-center font-semibold"
                />
                <Input
                  label="Niños"
                  type="text"
                  readOnly
                  value={String(reporte.nro_niños ?? 0)}
                  className="text-center font-semibold"
                />
                <Input
                  label="Visitas"
                  type="text"
                  readOnly
                  value={String(reporte.nro_visitas || 0)}
                  className="text-center font-semibold"
                />
                <Input
                  label="Comprometidos"
                  type="text"
                  readOnly
                  value={String(reporte.nro_comprometidos || 0)}
                  className="text-center font-semibold"
                />
              </div>
            </div>

            <div className="asistencia-total-pill">
              <span>Total Calculado:</span>
              <span className="total-number font-bold text-lg text-primary">{reporte.asistencia || 0}</span>
            </div>
          </div>

          {/* Columna Derecha: Frutos Espirituales y Ofrendas */}
          <div className="modal-section-card flex flex-col justify-between">
            <div>
              <h4 className="modal-section-title">
                <Icon name="attach_money" size={16} />
                <span>Ministerio y Recursos</span>
              </h4>

              <div className="grid grid-cols-2 gap-2 mb-2">
                <Input
                  label="Reconciliaciones"
                  type="text"
                  readOnly
                  value={String(reporte.reconciliaciones || 0)}
                  className="text-center font-semibold"
                />
                <Input
                  label="Confesiones"
                  type="text"
                  readOnly
                  value={String(reporte.confesiones || 0)}
                  className="text-center font-semibold"
                />
                <Input
                  label="Ofrendas en Dólares ($)"
                  type="text"
                  readOnly
                  value={`$ ${formatMoneda(reporte.ofrendas_usd)}`}
                  className="text-right font-bold text-primary dark:text-[#f3d07a]"
                />
                <Input
                  label="Ofrendas en Bolívares (Bs.)"
                  type="text"
                  readOnly
                  value={`Bs. ${formatMoneda(reporte.ofrendas_bs)}`}
                  className="text-right font-bold text-primary dark:text-[#f3d07a]"
                />
              </div>
            </div>

            <Input
              label="Cesta de Amor"
              type="text"
              readOnly
              value={tieneCesta ? 'Sí' : 'No'}
              className="text-center font-semibold"
            />
          </div>
        </div>

        {/* Observaciones */}
        <div className="modal-section-card">
          <label className="text-[11px] font-bold text-text-muted uppercase tracking-wider block mb-1">
            Observaciones
          </label>
          <textarea
            readOnly
            rows={2}
            className="w-full px-3 py-1.5 text-sm rounded-lg border border-border-subtle dark:border-[rgba(221,192,189,0.25)] bg-[#fbf8f8] dark:bg-[#150f10] text-text-main dark:text-[#f8f2f0] outline-none min-h-[48px] max-h-[90px] resize-none"
            value={reporte.observaciones || 'Sin observaciones registradas.'}
          />
        </div>
      </div>
    </Modal>
  );
};
