import React, { useState, useEffect, useMemo } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Icon } from '../ui/Icon';
import type { Reporte } from '../../types/reporte';

export interface ReporteModalProps {
  isOpen: boolean;
  onClose: () => void;
  reporte: Reporte | null;
  initialMode?: 'view' | 'edit';
  canEdit?: boolean;
  onGuardar: (id: string, data: Partial<Reporte>) => Promise<any>;
  isGuardando?: boolean;
}

export const ReporteModal: React.FC<ReporteModalProps> = ({
  isOpen,
  onClose,
  reporte,
  initialMode = 'view',
  canEdit = false,
  onGuardar,
  isGuardando = false,
}) => {
  const [mode, setMode] = useState<'view' | 'edit'>(initialMode);
  const [formError, setFormError] = useState<string | null>(null);

  // Estado del formulario para edición
  const [formData, setFormData] = useState({
    fecha: '',
    hr_inicio: '',
    hr_fin: '',
    tema: '',
    nro_regulares: 0,
    nro_ninos: 0,
    nro_visitas: 0,
    nro_comprometidos: 0,
    reconciliaciones: 0,
    confesiones: 0,
    ofrendas_usd: 0,
    ofrendas_bs: 0,
    cesta_amor: 0,
    observaciones: '',
  });

  // Sincronizar estado cuando cambia el reporte o se abre el modal
  useEffect(() => {
    if (reporte) {
      setMode(initialMode);
      setFormError(null);
      setFormData({
        fecha: reporte.fecha || '',
        hr_inicio: reporte.hr_inicio ? reporte.hr_inicio.slice(0, 5) : '18:00',
        hr_fin: reporte.hr_fin ? reporte.hr_fin.slice(0, 5) : '19:30',
        tema: reporte.tema || '',
        nro_regulares: reporte.nro_regulares || 0,
        nro_ninos: reporte.nro_ninos || 0,
        nro_visitas: reporte.nro_visitas || 0,
        nro_comprometidos: reporte.nro_comprometidos || 0,
        reconciliaciones: reporte.reconciliaciones || 0,
        confesiones: reporte.confesiones || 0,
        ofrendas_usd: reporte.ofrendas_usd || 0,
        ofrendas_bs: reporte.ofrendas_bs || 0,
        cesta_amor: reporte.cesta_amor ? 1 : 0,
        observaciones: reporte.observaciones || '',
      });
    }
  }, [reporte, initialMode, isOpen]);

  // Cálculo reactivo de Asistencia Total
  const totalAsistenciaCalculada = useMemo(() => {
    return (
      Number(formData.nro_regulares || 0) +
      Number(formData.nro_ninos || 0) +
      Number(formData.nro_visitas || 0) +
      Number(formData.nro_comprometidos || 0)
    );
  }, [
    formData.nro_regulares,
    formData.nro_ninos,
    formData.nro_visitas,
    formData.nro_comprometidos,
  ]);

  if (!reporte) return null;

  // Formato 12 horas AM/PM para modo vista
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

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    if (formError) setFormError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reporte) return;

    if (!formData.hr_inicio || !formData.hr_fin) {
      setFormError('Los horarios de inicio y fin son obligatorios.');
      return;
    }
    if (formData.hr_fin <= formData.hr_inicio) {
      setFormError('La hora de fin debe ser posterior a la hora de inicio.');
      return;
    }
    if (totalAsistenciaCalculada <= 0) {
      setFormError('La asistencia total calculada debe ser mayor a 0.');
      return;
    }

    const payload: Partial<Reporte> = {
      cdp_id: reporte.cdp_id,
      fecha: formData.fecha,
      hr_inicio: formData.hr_inicio,
      hr_fin: formData.hr_fin,
      tema: formData.tema,
      nro_regulares: Number(formData.nro_regulares),
      nro_ninos: Number(formData.nro_ninos),
      nro_visitas: Number(formData.nro_visitas),
      nro_comprometidos: Number(formData.nro_comprometidos),
      reconciliaciones: Number(formData.reconciliaciones),
      confesiones: Number(formData.confesiones),
      ofrendas_usd: Number(formData.ofrendas_usd),
      ofrendas_bs: Number(formData.ofrendas_bs),
      cesta_amor: Number(formData.cesta_amor),
      observaciones: formData.observaciones,
    };

    try {
      await onGuardar(reporte.id, payload);
      onClose();
    } catch {
      // Error manejado en la vista/toast
    }
  };

  const isEdit = mode === 'edit';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      headerIcon={<Icon name={isEdit ? 'edit_document' : 'visibility'} size={22} />}
      title={isEdit ? 'Editar Reporte Semanal' : 'Detalle del Reporte'}
      maxWidth="2xl"
      footer={
        isEdit ? (
          <div className="flex items-center justify-end gap-3 w-full">
            <button
              type="button"
              className="btn-modal btn-modal-cancel"
              onClick={() => {
                setFormError(null);
                setMode('view');
              }}
              disabled={isGuardando}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-modal btn-modal-save"
              form="form-reporte-modal"
              disabled={isGuardando}
            >
              <Icon name="save" size={16} />
              <span>{isGuardando ? 'Guardando...' : 'Guardar Cambios'}</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between w-full">
            <div>
              {canEdit && (
                <button
                  type="button"
                  onClick={() => setMode('edit')}
                  className="btn-modal btn-modal-save"
                >
                  <Icon name="edit" size={16} />
                  <span>Editar Reporte</span>
                </button>
              )}
            </div>
            <button type="button" className="btn-modal btn-modal-cancel" onClick={onClose}>
              Cerrar
            </button>
          </div>
        )
      }
    >
      <form id="form-reporte-modal" onSubmit={handleSubmit} className="flex flex-col gap-3 py-1">
        {formError && (
          <div className="p-3 bg-red-100 dark:bg-red-950/40 border border-red-300 dark:border-red-900/60 text-red-700 dark:text-red-300 rounded-lg text-xs font-semibold">
            {formError}
          </div>
        )}

        {/* Sección 1: Fecha y Encargado */}
        <div className="modal-section-card">
          <h4 className="modal-section-title">
            <Icon name="calendar_today" size={16} />
            <span>Fecha y Encargado</span>
          </h4>

          {isEdit ? (
            <div className="flex flex-col gap-3">
              <div className="modal-grid-2">
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Líder</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.lider_nombre}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Casa de Paz</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.cdp_codigo} · {reporte.cdp_nombre}
                  </p>
                </div>
              </div>

              <div className="modal-grid-2">
                <Input
                  label="Fecha de Reunión"
                  type="date"
                  value={formData.fecha}
                  onChange={(e) => handleInputChange('fecha', e.target.value)}
                  required
                />
                <Input
                  label="Tema de la Clase"
                  value={formData.tema}
                  onChange={(e) => handleInputChange('tema', e.target.value)}
                  placeholder="Ej. La obediencia y la bendición"
                  required
                />
              </div>

              <div className="modal-grid-2">
                <Input
                  label="Hora de Inicio"
                  type="time"
                  value={formData.hr_inicio}
                  onChange={(e) => handleInputChange('hr_inicio', e.target.value)}
                  required
                />
                <Input
                  label="Hora de Fin"
                  type="time"
                  value={formData.hr_fin}
                  onChange={(e) => handleInputChange('hr_fin', e.target.value)}
                  required
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-2.5">
              <div className="modal-grid-2">
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Líder Encargado</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.lider_nombre}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Casa de Paz</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.cdp_codigo} · {reporte.cdp_nombre}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Fecha de Reunión</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.fecha_formateada || reporte.fecha}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Horario</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {formatTime12h(reporte.hr_inicio)} – {formatTime12h(reporte.hr_fin)}
                  </p>
                </div>
              </div>
              <div className="mt-2 pt-2 border-t border-border-subtle/50 dark:border-[rgba(221,192,189,0.15)]">
                <span className="block text-[11px] font-bold text-text-muted uppercase">Tema Desarrollado</span>
                <p className="text-sm font-medium text-text-main dark:text-[#f8f2f0] mt-0.5">
                  {reporte.tema || 'Sin tema registrado'}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Sección 2: Asistencia y Desglose */}
        <div className="modal-section-card">
          <h4 className="modal-section-title">
            <Icon name="groups" size={16} />
            <span>Asistencia y Desglose</span>
          </h4>

          {isEdit ? (
            <div>
              <div className="modal-grid-4">
                <Input
                  label="Regulares"
                  type="number"
                  min="0"
                  value={formData.nro_regulares}
                  onChange={(e) => handleInputChange('nro_regulares', Number(e.target.value))}
                />
                <Input
                  label="Niños"
                  type="number"
                  min="0"
                  value={formData.nro_ninos}
                  onChange={(e) => handleInputChange('nro_ninos', Number(e.target.value))}
                />
                <Input
                  label="Visitas"
                  type="number"
                  min="0"
                  value={formData.nro_visitas}
                  onChange={(e) => handleInputChange('nro_visitas', Number(e.target.value))}
                />
                <Input
                  label="Comprometidos"
                  type="number"
                  min="0"
                  value={formData.nro_comprometidos}
                  onChange={(e) => handleInputChange('nro_comprometidos', Number(e.target.value))}
                />
              </div>

              <div className="asistencia-total-pill">
                <span>Asistencia Total Calculada:</span>
                <span className="total-number">{totalAsistenciaCalculada}</span>
              </div>
            </div>
          ) : (
            <div>
              <div className="modal-grid-4">
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Regulares</span>
                  <p className="text-base font-bold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.nro_regulares || 0}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Niños</span>
                  <p className="text-base font-bold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.nro_ninos || 0}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Visitas</span>
                  <p className="text-base font-bold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.nro_visitas || 0}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Comprometidos</span>
                  <p className="text-base font-bold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.nro_comprometidos || 0}
                  </p>
                </div>
              </div>

              <div className="asistencia-total-pill">
                <span>Total Calculado:</span>
                <span className="total-number">{reporte.asistencia || 0}</span>
              </div>
            </div>
          )}
        </div>

        {/* Sección 3: Ministerio y Recursos */}
        <div className="modal-section-card">
          <h4 className="modal-section-title">
            <Icon name="attach_money" size={16} />
            <span>Ministerio y Recursos</span>
          </h4>

          {isEdit ? (
            <div className="flex flex-col gap-3">
              <div className="modal-grid-2">
                <Input
                  label="Reconciliaciones"
                  type="number"
                  min="0"
                  value={formData.reconciliaciones}
                  onChange={(e) => handleInputChange('reconciliaciones', Number(e.target.value))}
                />
                <Input
                  label="Confesiones de Fe"
                  type="number"
                  min="0"
                  value={formData.confesiones}
                  onChange={(e) => handleInputChange('confesiones', Number(e.target.value))}
                />
              </div>

              <div className="modal-grid-2">
                <Input
                  label="Ofrendas en Dólares ($)"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.ofrendas_usd}
                  onChange={(e) => handleInputChange('ofrendas_usd', Number(e.target.value))}
                />
                <Input
                  label="Ofrendas en Bolívares (Bs.)"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.ofrendas_bs}
                  onChange={(e) => handleInputChange('ofrendas_bs', Number(e.target.value))}
                />
              </div>

              <Select
                label="¿Hubo Cesta de Amor?"
                value={String(formData.cesta_amor)}
                onChange={(e) => handleInputChange('cesta_amor', Number(e.target.value))}
                options={[
                  { value: '0', label: 'No' },
                  { value: '1', label: 'Sí' },
                ]}
              />

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-text-main dark:text-[#f8deda]">
                  Observaciones
                </label>
                <textarea
                  className="w-full px-3 py-2 text-sm rounded-lg border border-border-subtle dark:border-[rgba(221,192,189,0.25)] bg-white dark:bg-[#150f10] text-text-main dark:text-[#f8f2f0] focus:ring-2 focus:ring-[#700204] dark:focus:ring-[#f8deda] outline-none min-h-[65px]"
                  value={formData.observaciones}
                  onChange={(e) => handleInputChange('observaciones', e.target.value)}
                  placeholder="Sin observaciones adicionales."
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-2.5">
              <div className="modal-grid-2">
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Reconciliaciones</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.reconciliaciones || 0}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Confesiones de Fe</span>
                  <p className="text-sm font-semibold text-text-main dark:text-[#f8f2f0] mt-0.5">
                    {reporte.confesiones || 0}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Ofrendas en Dólares ($)</span>
                  <p className="text-sm font-bold text-primary dark:text-[#f3d07a] mt-0.5">
                    ${Number(reporte.ofrendas_usd || 0).toFixed(2)}
                  </p>
                </div>
                <div>
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Ofrendas en Bolívares (Bs.)</span>
                  <p className="text-sm font-bold text-primary dark:text-[#f3d07a] mt-0.5">
                    Bs. {Number(reporte.ofrendas_bs || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
              </div>

              <div className="mt-2 pt-2 border-t border-border-subtle/50 dark:border-[rgba(221,192,189,0.15)]">
                <span className="block text-[11px] font-bold text-text-muted uppercase">Cesta de Amor</span>
                <p className="text-sm font-medium text-text-main dark:text-[#f8f2f0] mt-0.5">
                  {reporte.cesta_amor ? 'Sí' : 'No'}
                </p>
              </div>

              {reporte.observaciones && (
                <div className="mt-2 pt-2 border-t border-border-subtle/50 dark:border-[rgba(221,192,189,0.15)]">
                  <span className="block text-[11px] font-bold text-text-muted uppercase">Observaciones</span>
                  <p className="text-sm font-medium text-text-main dark:text-[#f8f2f0] mt-0.5 italic">
                    "{reporte.observaciones}"
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </form>
    </Modal>
  );
};
