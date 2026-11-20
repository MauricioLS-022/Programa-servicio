import { useState, useMemo, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useReportes } from './useReportes';
import { useAuth } from './useAuth';
import { usePerfil } from './usePerfil';
import { useCasasDePaz, useLideres } from './useDashboard';
import { useToast } from '../context/ToastContext';

/**
 * Hook controlador para el formulario de generación de reportes ministeriales.
 * Centraliza estado de campos, cálculo reactivo de asistencia total, validaciones
 * y envío idempotente manteniendo 100% paridad con generar_reporte.html.
 */
export function useGenerarReporteForm() {
  const { user } = useAuth();
  const { perfil, isLoading: isPerfilLoading } = usePerfil();
  const { crearReporte, isCreando } = useReportes();
  const { success, error } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const todayStr = useMemo(() => new Date().toISOString().split('T')[0], []);

  const initialCdpId = useMemo(() => {
    const fromParam = searchParams.get('cdp_id');
    if (fromParam) return Number(fromParam);
    if (perfil?.cdp_id) return perfil.cdp_id;
    return undefined;
  }, [searchParams, perfil]);

  const [selectedCdpId, setSelectedCdpId] = useState<number | undefined>(initialCdpId);

  useEffect(() => {
    if (initialCdpId && !selectedCdpId) {
      setSelectedCdpId(initialCdpId);
    }
  }, [initialCdpId, selectedCdpId]);

  const { casas } = useCasasDePaz();
  const { lideres } = useLideres({ cdp_id: selectedCdpId });

  const [liderId, setLiderId] = useState<string>('');
  const [fecha] = useState<string>(todayStr);
  const [hrInicio, setHrInicio] = useState<string>('');
  const [hrFin, setHrFin] = useState<string>('');

  const [nroRegulares, setNroRegulares] = useState<number | ''>('');
  const [nroNinos, setNroNinos] = useState<number | ''>('');
  const [nroVisitas, setNroVisitas] = useState<number | ''>('');
  const [nroComprometidos, setNroComprometidos] = useState<number | ''>('');

  const [reconciliaciones, setReconciliaciones] = useState<number | ''>('');
  const [confesiones, setConfesiones] = useState<number | ''>('');

  const [ofrendasBs, setOfrendasBs] = useState<string>('');
  const [ofrendasUsd, setOfrendasUsd] = useState<string>('');
  const [cestaAmor, setCestaAmor] = useState<number>(0);

  const [tema, setTema] = useState<string>('');
  const [observaciones, setObservaciones] = useState<string>('');

  const totalAsistencia = useMemo(() => {
    const reg = Number(nroRegulares) || 0;
    const nin = Number(nroNinos) || 0;
    const vis = Number(nroVisitas) || 0;
    const com = Number(nroComprometidos) || 0;
    return reg + nin + vis + com;
  }, [nroRegulares, nroNinos, nroVisitas, nroComprometidos]);

  const returnUrl = user?.rol === 'admin' ? '/reportes' : '/dashboard';

  const cdpInfo = useMemo(() => {
    if (user?.rol === 'admin' && selectedCdpId) {
      const match = casas.find((c) => c.id === selectedCdpId);
      if (match) return { codigo: match.codigo, nombre: match.nombre || match.anfitrion || 'Casa de Paz' };
    }
    if (perfil?.cdp_codigo) {
      return { codigo: perfil.cdp_codigo, nombre: perfil.cdp_nombre || perfil.cdp_anfitrion || 'Casa de Paz' };
    }
    return null;
  }, [user?.rol, selectedCdpId, casas, perfil]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      const effectiveCdpId = user?.rol === 'admin' ? selectedCdpId : (perfil?.cdp_id || selectedCdpId);
      if (!effectiveCdpId) {
        error(
          user?.rol === 'admin'
            ? 'Debes seleccionar la Casa de Paz que reporta.'
            : 'No se encontró una Casa de Paz asignada para registrar este reporte.'
        );
        return;
      }

      if (!hrInicio || !hrFin) {
        error('Debes ingresar la hora de inicio y de finalización.');
        return;
      }

      if (hrFin <= hrInicio) {
        error('La hora de finalización debe ser posterior a la hora de inicio.');
        return;
      }

      const temaTrim = tema.trim();
      if (!temaTrim || temaTrim.length < 2) {
        error('El tema desarrollado es obligatorio y debe tener al menos 2 caracteres.');
        return;
      }

      if (totalAsistencia <= 0) {
        error('Debes registrar al menos un asistente en la reunión.');
        return;
      }

      const bsNum = ofrendasBs === '' ? 0 : parseFloat(ofrendasBs);
      const usdNum = ofrendasUsd === '' ? 0 : parseFloat(ofrendasUsd);

      if (isNaN(bsNum) || bsNum < 0) {
        error('El monto en Bolívares (Bs.) debe ser un número válido mayor o igual a cero.');
        return;
      }
      if (isNaN(usdNum) || usdNum < 0) {
        error('El monto en USD ($) debe ser un número válido mayor o igual a cero.');
        return;
      }

      try {
        const payload = {
          cdp_id: effectiveCdpId,
          lider_id: liderId ? Number(liderId) : undefined,
          fecha,
          hr_inicio: hrInicio,
          hr_fin: hrFin,
          tema: temaTrim,
          nro_regulares: Number(nroRegulares) || 0,
          nro_ninos: Number(nroNinos) || 0,
          nro_visitas: Number(nroVisitas) || 0,
          nro_comprometidos: Number(nroComprometidos) || 0,
          reconciliaciones: Number(reconciliaciones) || 0,
          confesiones: Number(confesiones) || 0,
          cesta_amor: cestaAmor,
          ofrendas_usd: usdNum,
          ofrendas_bs: bsNum,
          observaciones: observaciones.trim() || undefined,
        };

        const res = await crearReporte(payload);
        if (res.success) {
          success('¡Reporte ministerial registrado exitosamente!');
          navigate(returnUrl);
        } else {
          error(res.error || 'No se pudo guardar el reporte ministerial.');
        }
      } catch (err: unknown) {
        if (err instanceof Error) {
          error(err.message || 'Error de conexión al procesar el reporte.');
        } else {
          error('Error inesperado al guardar el reporte.');
        }
      }
    },
    [
      user?.rol,
      selectedCdpId,
      perfil?.cdp_id,
      hrInicio,
      hrFin,
      tema,
      totalAsistencia,
      ofrendasBs,
      ofrendasUsd,
      liderId,
      fecha,
      nroRegulares,
      nroNinos,
      nroVisitas,
      nroComprometidos,
      reconciliaciones,
      confesiones,
      cestaAmor,
      observaciones,
      crearReporte,
      success,
      error,
      navigate,
      returnUrl,
    ]
  );

  const sinCdpAsignada = !isPerfilLoading && user?.rol === 'lider_cdp' && !perfil?.cdp_id;

  return {
    user,
    perfil,
    isPerfilLoading,
    isCreando,
    sinCdpAsignada,
    casas,
    lideres,
    cdpInfo,
    returnUrl,
    navigate,
    selectedCdpId,
    setSelectedCdpId,
    liderId,
    setLiderId,
    fecha,
    hrInicio,
    setHrInicio,
    hrFin,
    setHrFin,
    nroRegulares,
    setNroRegulares,
    nroNinos,
    setNroNinos,
    nroVisitas,
    setNroVisitas,
    nroComprometidos,
    setNroComprometidos,
    reconciliaciones,
    setReconciliaciones,
    confesiones,
    setConfesiones,
    ofrendasBs,
    setOfrendasBs,
    ofrendasUsd,
    setOfrendasUsd,
    cestaAmor,
    setCestaAmor,
    tema,
    setTema,
    observaciones,
    setObservaciones,
    totalAsistencia,
    handleSubmit,
  };
}
