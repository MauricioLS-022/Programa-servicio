import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useReportes } from '../hooks/useReportes';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../context/ToastContext';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import {
  FileText,
  DollarSign,
  Users,
  CheckCircle2,
  Calendar,
} from 'lucide-react';

export const GenerarReportePage: React.FC = () => {
  const { user } = useAuth();
  const { crearReporte, isCreando } = useReportes();
  const { success, error } = useToast();
  const navigate = useNavigate();

  const todayStr = new Date().toISOString().split('T')[0];

  // Form State
  const [fecha, setFecha] = useState(todayStr);
  const [tema, setTema] = useState('');
  const [hermanos, setHermanos] = useState<number | ''>('');
  const [amigos, setAmigos] = useState<number | ''>('');
  const [ninos, setNinos] = useState<number | ''>('');

  const [efectivoUsd, setEfectivoUsd] = useState<number | ''>('');
  const [efectivoBs, setEfectivoBs] = useState<number | ''>('');
  const [digitalUsd, setDigitalUsd] = useState<number | ''>('');
  const [digitalBs, setDigitalBs] = useState<number | ''>('');
  const [tasaCambio, setTasaCambio] = useState<number | ''>(40.0); // Tasa referencial por defecto

  const [motivoOracion, setMotivoOracion] = useState('');
  const [observaciones, setObservaciones] = useState('');
  const [cestaAmor, setCestaAmor] = useState(false);
  const [cdpIdAdmin, setCdpIdAdmin] = useState<number | ''>('');

  // Cálculos dinámicos en tiempo real (Paridad con generar_reporte.js)
  const totalAsistencia = useMemo(() => {
    const h = Number(hermanos) || 0;
    const a = Number(amigos) || 0;
    const n = Number(ninos) || 0;
    return h + a + n;
  }, [hermanos, amigos, ninos]);

  const totalOfrendaUsd = useMemo(() => {
    const efUsd = Number(efectivoUsd) || 0;
    const digUsd = Number(digitalUsd) || 0;
    return efUsd + digUsd;
  }, [efectivoUsd, digitalUsd]);

  const totalOfrendaBs = useMemo(() => {
    const efBs = Number(efectivoBs) || 0;
    const digBs = Number(digitalBs) || 0;
    return efBs + digBs;
  }, [efectivoBs, digitalBs]);

  const totalConsolidadoUsd = useMemo(() => {
    const tasa = Number(tasaCambio) || 1;
    const bsEnUsd = tasa > 0 ? totalOfrendaBs / tasa : 0;
    return totalOfrendaUsd + bsEnUsd;
  }, [totalOfrendaUsd, totalOfrendaBs, tasaCambio]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!fecha) {
      error('La fecha de reunión es obligatoria');
      return;
    }

    if (totalAsistencia <= 0) {
      error('Debes registrar al menos un asistente en la reunión');
      return;
    }

    try {
      const payload = {
        cdp_id: user?.rol === 'admin' && cdpIdAdmin ? Number(cdpIdAdmin) : undefined,
        fecha,
        tema: tema.trim() || undefined,
        asistencia: totalAsistencia,
        hermanos: Number(hermanos) || 0,
        amigos: Number(amigos) || 0,
        ninos: Number(ninos) || 0,
        ofrenda_efectivo_usd: Number(efectivoUsd) || 0,
        ofrenda_efectivo_bs: Number(efectivoBs) || 0,
        ofrenda_digital_usd: Number(digitalUsd) || 0,
        ofrenda_digital_bs: Number(digitalBs) || 0,
        tasa_cambio: Number(tasaCambio) || 0,
        motivo_oracion: motivoOracion.trim() || undefined,
        observaciones: observaciones.trim() || undefined,
        cesta_amor: cestaAmor ? 1 : 0,
      };

      const res = await crearReporte(payload);
      if (res.success) {
        success('¡Reporte ministerial registrado exitosamente!');
        navigate('/reportes');
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        error(err.message || 'Error al guardar el reporte');
      } else {
        error('Error al registrar el reporte');
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div>
        <h1 className="font-serif text-2xl sm:text-3xl font-bold text-text-main dark:text-neutral-100 tracking-tight">
          Planilla de Reporte Ministerial
        </h1>
        <p className="text-xs sm:text-sm text-text-muted dark:text-neutral-400 mt-1">
          Carga semanal de asistencia, frutos y ofrendas de Casa de Paz
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        {/* Sección: Datos Generales */}
        <Card
          title="1. Datos de la Reunión"
          subtitle="Identificación y fecha de celebración"
          icon={<Calendar className="w-5 h-5" />}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Fecha de Celebración"
              type="date"
              value={fecha}
              max={todayStr}
              onChange={(e) => setFecha(e.target.value)}
              required
            />

            <Input
              label="Tema Ministrado"
              placeholder="Ej: Principios de la Fe"
              value={tema}
              onChange={(e) => setTema(e.target.value)}
            />

            {user?.rol === 'admin' && (
              <div className="sm:col-span-2">
                <Input
                  label="ID de Casa de Paz (Solo Admin)"
                  type="number"
                  placeholder="Ej: 1"
                  value={cdpIdAdmin}
                  onChange={(e) => setCdpIdAdmin(e.target.value ? Number(e.target.value) : '')}
                  helperText="Indica a qué Casa de Paz asignar este reporte"
                  required
                />
              </div>
            )}
          </div>
        </Card>

        {/* Sección: Asistencia y Fruto */}
        <Card
          title="2. Registro de Asistencia"
          subtitle="Desglose de asistentes por categoría"
          icon={<Users className="w-5 h-5" />}
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Input
              label="Hermanos"
              type="number"
              min="0"
              placeholder="0"
              value={hermanos}
              onChange={(e) => setHermanos(e.target.value ? Number(e.target.value) : '')}
            />

            <Input
              label="Nuevos Amigos (Visitas)"
              type="number"
              min="0"
              placeholder="0"
              value={amigos}
              onChange={(e) => setAmigos(e.target.value ? Number(e.target.value) : '')}
            />

            <Input
              label="Niños"
              type="number"
              min="0"
              placeholder="0"
              value={ninos}
              onChange={(e) => setNinos(e.target.value ? Number(e.target.value) : '')}
            />
          </div>

          <div className="mt-5 p-4 rounded-xl bg-surface-container/70 dark:bg-neutral-700/40 border border-border-subtle/80 dark:border-neutral-700 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-text-main dark:text-neutral-200">
              Total de Asistencia Calculado:
            </span>
            <span className="font-serif text-2xl font-extrabold text-vino dark:text-vino-light">
              {totalAsistencia} personas
            </span>
          </div>
        </Card>

        {/* Sección: Ofrendas Duales */}
        <Card
          title="3. Ofrendas Recaudadas (USD / Bs)"
          subtitle="Registro dual en efectivo y transferencias digitales"
          icon={<DollarSign className="w-5 h-5" />}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <Input
              label="Efectivo USD ($)"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={efectivoUsd}
              onChange={(e) => setEfectivoUsd(e.target.value ? Number(e.target.value) : '')}
            />

            <Input
              label="Efectivo Bolívares (Bs)"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={efectivoBs}
              onChange={(e) => setEfectivoBs(e.target.value ? Number(e.target.value) : '')}
            />

            <Input
              label="Digital / Transferencia USD ($)"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={digitalUsd}
              onChange={(e) => setDigitalUsd(e.target.value ? Number(e.target.value) : '')}
            />

            <Input
              label="Digital / Pago Móvil Bs"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={digitalBs}
              onChange={(e) => setDigitalBs(e.target.value ? Number(e.target.value) : '')}
            />

            <div className="sm:col-span-2">
              <Input
                label="Tasa de Cambio Referencial (Bs por USD)"
                type="number"
                step="0.01"
                min="0"
                value={tasaCambio}
                onChange={(e) => setTasaCambio(e.target.value ? Number(e.target.value) : '')}
                helperText="Utilizada para calcular el balance consolidado"
              />
            </div>
          </div>

          {/* Consolidado en Vivo */}
          <div className="p-4 rounded-xl bg-surface-low dark:bg-neutral-800/80 border border-border-subtle dark:border-neutral-700 grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
            <div>
              <p className="text-[11px] font-bold uppercase text-text-muted dark:text-neutral-400">
                Total USD Recaudado
              </p>
              <p className="text-lg font-bold text-emerald-700 dark:text-emerald-400 mt-0.5">
                ${totalOfrendaUsd.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase text-text-muted dark:text-neutral-400">
                Total Bs Recaudado
              </p>
              <p className="text-lg font-bold text-blue-700 dark:text-blue-400 mt-0.5">
                Bs {totalOfrendaBs.toLocaleString('es-VE', { minimumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase text-text-muted dark:text-neutral-400">
                Consolidado Estimado USD
              </p>
              <p className="text-lg font-extrabold text-vino dark:text-vino-light mt-0.5">
                ${totalConsolidadoUsd.toFixed(2)}
              </p>
            </div>
          </div>
        </Card>

        {/* Sección: Observaciones & Cesta de Amor */}
        <Card
          title="4. Detalles y Cesta de Amor"
          subtitle="Comentarios, testimonios y apoyo fraterno"
          icon={<FileText className="w-5 h-5" />}
        >
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3 p-3 rounded-xl border border-border-subtle dark:border-neutral-700 bg-surface-low/40 dark:bg-neutral-800/40">
              <input
                id="cestaAmor"
                type="checkbox"
                checked={cestaAmor}
                onChange={(e) => setCestaAmor(e.target.checked)}
                className="w-4 h-4 text-vino rounded border-border-subtle focus:ring-vino cursor-pointer"
              />
              <label
                htmlFor="cestaAmor"
                className="text-xs font-semibold text-text-main dark:text-neutral-200 cursor-pointer"
              >
                ¿Se realizó entrega de Cesta de Amor en esta reunión?
              </label>
            </div>

            <Input
              label="Peticiones o Motivo de Oración"
              placeholder="Necesidades especiales o intenciones de oración"
              value={motivoOracion}
              onChange={(e) => setMotivoOracion(e.target.value)}
            />

            <Input
              label="Observaciones Generales"
              placeholder="Testimonios, novedades o incidencias durante la reunión"
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
            />
          </div>
        </Card>

        {/* Action Buttons with Idempotency Guard */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/reportes')}
            disabled={isCreando}
          >
            Cancelar
          </Button>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isCreando}
            icon={<CheckCircle2 className="w-5 h-5" />}
          >
            Enviar y Guardar Reporte
          </Button>
        </div>
      </form>
    </div>
  );
};
