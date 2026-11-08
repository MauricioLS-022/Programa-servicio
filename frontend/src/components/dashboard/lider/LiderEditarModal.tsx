import React, { useState, useEffect, useMemo } from 'react';
import { Modal } from '../../ui/Modal';
import { Icon } from '../../ui/Icon';
import { Input } from '../../ui/Input';
import { Select } from '../../ui/Select';
import { api } from '../../../api/client';
import type { LiderReporteItem, LiderMiembro } from '../../../types/liderDashboard';

export interface LiderEditarModalProps {
  isOpen: boolean;
  onClose: () => void;
  reporte: LiderReporteItem | null;
  lideres: LiderMiembro[];
  onSuccess: () => void;
}

export const LiderEditarModal: React.FC<LiderEditarModalProps> = ({
  isOpen,
  onClose,
  reporte,
  lideres,
  onSuccess,
}) => {
  const [formData, setFormData] = useState({
    lider_id: '',
    fecha: '',
    tema: '',
    hr_inicio: '',
    hr_fin: '',
    nro_regulares: 0,
    nro_ninos: 0,
    nro_visitas: 0,
    nro_comprometidos: 0,
    reconciliaciones: 0,
    confesiones: 0,
    ofrendas_usd: 0,
    ofrendas_bs: 0,
    cesta_amor: '0',
    observaciones: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (reporte) {
      setFormData({
        lider_id: String(reporte.enviado_por_lider_id || ''),
        fecha: reporte.fecha ? reporte.fecha.substring(0, 10) : '',
        tema: reporte.tema || '',
        hr_inicio: reporte.hr_inicio ? reporte.hr_inicio.slice(0, 5) : '',
        hr_fin: reporte.hr_fin ? reporte.hr_fin.slice(0, 5) : '',
        nro_regulares: Number(reporte.nro_regulares || 0),
        nro_ninos: Number(reporte.nro_niños || 0),
        nro_visitas: Number(reporte.nro_visitas || 0),
        nro_comprometidos: Number(reporte.nro_comprometidos || 0),
        reconciliaciones: Number(reporte.reconciliaciones || 0),
        confesiones: Number(reporte.confesiones || 0),
        ofrendas_usd: Number(reporte.ofrendas_usd || 0),
        ofrendas_bs: Number(reporte.ofrendas_bs || 0),
        cesta_amor:
          reporte.cesta_amor === true ||
          reporte.cesta_amor === 1 ||
          reporte.cesta_amor === '1' ||
          String(reporte.cesta_amor || '').trim().toLowerCase() === 'sí' ||
          String(reporte.cesta_amor || '').trim().toLowerCase() === 'si'
            ? '1'
            : '0',
        observaciones: reporte.observaciones || '',
      });
      setErrorMessage(null);
    }
  }, [reporte]);

  const totalAsistencia = useMemo(() => {
    return (
      (Number(formData.nro_regulares) || 0) +
      (Number(formData.nro_ninos) || 0) +
      (Number(formData.nro_visitas) || 0) +
      (Number(formData.nro_comprometidos) || 0)
    );
  }, [
    formData.nro_regulares,
    formData.nro_ninos,
    formData.nro_visitas,
    formData.nro_comprometidos,
  ]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reporte) return;

    if (!formData.hr_inicio || !formData.hr_fin) {
      setErrorMessage('Los horarios de inicio y fin son obligatorios.');
      return;
    }
    if (formData.hr_fin <= formData.hr_inicio) {
      setErrorMessage('La hora de fin debe ser posterior a la hora de inicio.');
      return;
    }
    if (totalAsistencia <= 0) {
      setErrorMessage('La asistencia total calculada debe ser mayor a 0.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      await api.put(`/reportes/${reporte.id}`, {
        ...formData,
        asistencia: totalAsistencia,
        cesta_amor: formData.cesta_amor === '1' ? 'Sí' : 'No',
      });
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Error al actualizar el reporte. Verifica los datos introducidos.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  if (!reporte) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Editar Reporte Semanal"
      headerIcon={
        <div className="modal-header-icon">
          <Icon name="edit_document" size={20} />
        </div>
      }
      maxWidth="lg"
      footer={
        <div className="flex items-center justify-end gap-3 w-full">
          <button
            type="button"
            className="btn-modal btn-modal-cancel"
            onClick={onClose}
            disabled={isLoading}
            data-testid="btn-cancelar-editar"
          >
            Cancelar
          </button>
          <button
            type="submit"
            form="formEditarReporte"
            className="btn-modal btn-modal-save"
            disabled={isLoading}
            data-testid="btn-guardar-editar"
          >
            <Icon name="save" size={16} />
            <span>{isLoading ? 'Guardando...' : 'Guardar Cambios'}</span>
          </button>
        </div>
      }
    >
      <form id="formEditarReporte" onSubmit={handleSubmit} className="flex flex-col gap-2.5 py-0.5">
        <div data-testid="lider-modal-editar-body" className="flex flex-col gap-2.5">
          {errorMessage && (
            <div
              style={{
                background: 'var(--danger-bg, #fee2e2)',
                color: 'var(--danger-color, #b32626)',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.88rem',
                fontWeight: 600,
              }}
            >
              {errorMessage}
            </div>
          )}

          {/* Sección 1: Fecha y Encargado */}
          <div className="modal-section-card">
            <h4 className="modal-section-title">
              <Icon name="calendar_today" size={16} />
              <span>Fecha y Encargado</span>
            </h4>

            <div className="flex flex-col gap-2.5">
              <Select
                label="Líder Encargado *"
                id="editLiderId"
                name="lider_id"
                value={formData.lider_id}
                onChange={handleChange}
                options={[
                  { value: '', label: 'Selecciona el líder encargado...' },
                  ...lideres.map((l) => ({
                    value: String(l.id),
                    label: `${l.nombre} ${l.apellido || ''} (${l.rol})`,
                  })),
                ]}
                required
              />

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <Input
                  label="Fecha de Reunión *"
                  id="editFecha"
                  name="fecha"
                  type="date"
                  value={formData.fecha}
                  onChange={handleChange}
                  required
                />
                <Input
                  label="Hora de Inicio *"
                  id="editHrInicio"
                  name="hr_inicio"
                  type="time"
                  value={formData.hr_inicio}
                  onChange={handleChange}
                  required
                />
                <Input
                  label="Hora de Fin *"
                  id="editHrFin"
                  name="hr_fin"
                  type="time"
                  value={formData.hr_fin}
                  onChange={handleChange}
                  required
                />
              </div>

              <Input
                label="Tema de la Clase *"
                id="editTema"
                name="tema"
                type="text"
                value={formData.tema}
                onChange={handleChange}
                placeholder="Ej. La obediencia y la bendición"
                required
              />
            </div>
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
                    id="editRegulares"
                    name="nro_regulares"
                    type="number"
                    min="0"
                    value={formData.nro_regulares}
                    onChange={handleChange}
                  />
                  <Input
                    label="Niños"
                    id="editNinos"
                    name="nro_ninos"
                    type="number"
                    min="0"
                    value={formData.nro_ninos}
                    onChange={handleChange}
                  />
                  <Input
                    label="Visitas"
                    id="editVisitas"
                    name="nro_visitas"
                    type="number"
                    min="0"
                    value={formData.nro_visitas}
                    onChange={handleChange}
                  />
                  <Input
                    label="Comprometidos"
                    id="editComprometidos"
                    name="nro_comprometidos"
                    type="number"
                    min="0"
                    value={formData.nro_comprometidos}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="asistencia-total-pill">
                <span>Asistencia Total Calculada:</span>
                <span className="total-number font-bold text-lg text-primary">{totalAsistencia}</span>
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
                    id="editReconciliaciones"
                    name="reconciliaciones"
                    type="number"
                    min="0"
                    value={formData.reconciliaciones}
                    onChange={handleChange}
                  />
                  <Input
                    label="Confesiones"
                    id="editConfesiones"
                    name="confesiones"
                    type="number"
                    min="0"
                    value={formData.confesiones}
                    onChange={handleChange}
                  />
                  <Input
                    label="Ofrendas ($)"
                    id="editOfrendasUsd"
                    name="ofrendas_usd"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.ofrendas_usd}
                    onChange={handleChange}
                  />
                  <Input
                    label="Ofrendas (Bs.)"
                    id="editOfrendasBs"
                    name="ofrendas_bs"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.ofrendas_bs}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <Select
                label="¿Cesta de Amor? *"
                id="editCestaAmor"
                name="cesta_amor"
                value={String(formData.cesta_amor)}
                onChange={handleChange}
                options={[
                  { value: '0', label: 'No' },
                  { value: '1', label: 'Sí' },
                ]}
                required
              />
            </div>
          </div>

          {/* Observaciones */}
          <div className="modal-section-card">
            <label className="text-[11px] font-bold text-text-muted uppercase tracking-wider block mb-1">
              Observaciones
            </label>
            <textarea
              id="editObservaciones"
              name="observaciones"
              rows={2}
              className="w-full px-3 py-1.5 text-sm rounded-lg border border-border-subtle dark:border-[rgba(221,192,189,0.25)] bg-white dark:bg-[#150f10] text-text-main dark:text-[#f8f2f0] focus:ring-2 focus:ring-[#700204] dark:focus:ring-[#f8deda] outline-none min-h-[48px] max-h-[90px] resize-none"
              value={formData.observaciones}
              onChange={handleChange}
              placeholder="Sin observaciones adicionales."
            />
          </div>
        </div>
      </form>
    </Modal>
  );
};
