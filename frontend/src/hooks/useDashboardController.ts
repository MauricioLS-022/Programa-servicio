import { useMemo, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import { useUrlFilters } from './useUrlFilters';
import { useDashboard, useRedes, useCasasDePaz } from './useDashboard';
import type { PeriodoTipo } from '../components/dashboard/DashboardPeriodToggle';

export type DashboardNivel = 'general' | 'red' | 'cdp';

interface DashboardFilters extends Record<string, string | number | boolean | null | undefined> {
  nivel: DashboardNivel;
  periodo: PeriodoTipo;
  red_id: string;
  cdp_id: string;
  q: string;
}

/**
 * Hook controlador para el Dashboard Administrativo y Regional.
 * Encapsula la derivación de rol supervisor, sincronización bidireccional URL (SSOT),
 * filtrado rápido de Casas de Paz y transiciones atómicas entre niveles jerárquicos.
 */
export function useDashboardController() {
  const { user } = useAuth();
  const isSupervisor = user?.rol === 'supervisor';

  const { redes } = useRedes();
  const { casas: allCasas } = useCasasDePaz();

  const supervisorRedId = useMemo(() => {
    return isSupervisor && redes.length > 0 ? String(redes[0].id) : '';
  }, [isSupervisor, redes]);

  const defaultNivel: DashboardNivel = isSupervisor ? 'red' : 'general';

  const defaults = useMemo<DashboardFilters>(
    () => ({
      nivel: defaultNivel,
      periodo: 'semana',
      red_id: isSupervisor ? supervisorRedId : '',
      cdp_id: '',
      q: '',
    }),
    [defaultNivel, isSupervisor, supervisorRedId]
  );

  const { filters, setFilter, setFilters, resetFilters } = useUrlFilters(defaults);

  const rawNivel = (filters.nivel as DashboardNivel) || defaultNivel;
  const nivel: DashboardNivel = isSupervisor && rawNivel === 'general' ? 'red' : rawNivel;
  const periodo: PeriodoTipo = (filters.periodo as PeriodoTipo) || 'semana';
  const redId: string = String(filters.red_id || (isSupervisor ? supervisorRedId : ''));
  const cdpId: string = String(filters.cdp_id || '');
  const searchQuery: string = String(filters.q || '');

  const { metricas, isLoading, isError, error, refetch } = useDashboard({
    nivel,
    red_id: redId || undefined,
    cdp_id: cdpId || undefined,
    periodo,
  });

  // Candado reactivo para supervisor: impedir nivel 'general' o pérdida de su red asignada
  useEffect(() => {
    if (isSupervisor) {
      if (filters.nivel === 'general') {
        setFilter('nivel', 'red');
      }
      if (supervisorRedId && (!filters.red_id || (filters.red_id !== supervisorRedId && nivel === 'red'))) {
        setFilter('red_id', supervisorRedId);
      }
    }
  }, [isSupervisor, filters.nivel, filters.red_id, supervisorRedId, nivel, setFilter]);

  const filteredCasas = useMemo(() => {
    if (!searchQuery.trim()) return allCasas;
    const q = searchQuery.toLowerCase().trim();
    return allCasas.filter(
      (c) =>
        c.codigo?.toLowerCase().includes(q) ||
        c.anfitrion?.toLowerCase().includes(q) ||
        c.red_nombre?.toLowerCase().includes(q)
    );
  }, [allCasas, searchQuery]);

  // Auto-selección y aislamiento estricto de Red y Casa de Paz al conmutar niveles
  useEffect(() => {
    if (nivel === 'red') {
      if (cdpId) {
        setFilter('cdp_id', '');
      }
      if (!redId && redes.length > 0) {
        setFilter('red_id', String(redes[0].id));
      }
    } else if (nivel === 'cdp') {
      const activeRed = redId || (redes.length > 0 ? String(redes[0].id) : '');
      if (!redId && activeRed) {
        setFilter('red_id', activeRed);
      }
      const candidateCasas = activeRed
        ? allCasas.filter((c) => String(c.red_id) === String(activeRed))
        : allCasas;

      const currentValid = candidateCasas.some((c) => String(c.id) === String(cdpId));
      if (!currentValid) {
        if (candidateCasas.length > 0) {
          setFilter('cdp_id', String(candidateCasas[0].id));
        } else {
          setFilter('cdp_id', '');
        }
      }
    }
  }, [nivel, redId, cdpId, redes, allCasas, setFilter]);

  const handleNivelChange = useCallback(
    (newNivel: DashboardNivel) => {
      if (isSupervisor) {
        const targetRed = supervisorRedId || redId || (redes.length > 0 ? String(redes[0].id) : '');
        if (newNivel === 'cdp') {
          const candidateCasas = targetRed
            ? allCasas.filter((c) => String(c.red_id) === String(targetRed))
            : allCasas;
          const firstCdpId = candidateCasas.length > 0 ? String(candidateCasas[0].id) : '';
          setFilters({ nivel: 'cdp', red_id: targetRed, cdp_id: firstCdpId });
        } else {
          setFilters({ nivel: 'red', red_id: targetRed, cdp_id: '' });
        }
        return;
      }

      if (newNivel === 'general') {
        setFilters({ nivel: 'general', red_id: '', cdp_id: '' });
      } else if (newNivel === 'red') {
        const targetRedId = redId || (redes.length > 0 ? String(redes[0].id) : '');
        setFilters({ nivel: 'red', red_id: targetRedId, cdp_id: '' });
      } else if (newNivel === 'cdp') {
        const activeRed = redId || (redes.length > 0 ? String(redes[0].id) : '');
        const candidateCasas = activeRed
          ? allCasas.filter((c) => String(c.red_id) === String(activeRed))
          : allCasas;
        const firstCdpId = candidateCasas.length > 0 ? String(candidateCasas[0].id) : '';
        setFilters({ nivel: 'cdp', red_id: activeRed, cdp_id: firstCdpId });
      }
    },
    [isSupervisor, supervisorRedId, redId, redes, allCasas, setFilters]
  );

  const handleRedChange = useCallback(
    (newRedId: string | number) => {
      if (isSupervisor) return;
      const redStr = String(newRedId || '');
      if (nivel === 'cdp') {
        if (redStr) {
          const candidateCasas = allCasas.filter((c) => String(c.red_id) === redStr);
          const firstCdpId = candidateCasas.length > 0 ? String(candidateCasas[0].id) : '';
          setFilters({ red_id: redStr, cdp_id: firstCdpId });
        } else {
          setFilters({ red_id: '', cdp_id: '' });
        }
      } else {
        setFilters({ red_id: redStr, cdp_id: '' });
      }
    },
    [isSupervisor, nivel, allCasas, setFilters]
  );

  const handleCdpChange = useCallback(
    (newCdpId: string | number) => {
      setFilter('cdp_id', String(newCdpId || ''));
    },
    [setFilter]
  );

  const handleSearchChange = useCallback(
    (q: string) => {
      setFilter('q', q);
    },
    [setFilter]
  );

  const handlePeriodoChange = useCallback(
    (newPeriodo: PeriodoTipo) => {
      setFilter('periodo', newPeriodo);
    },
    [setFilter]
  );

  const handleSelectRedFromRanking = useCallback(
    (selectedRedId: string | number) => {
      setFilters({ nivel: 'red', red_id: String(selectedRedId), cdp_id: '' });
    },
    [setFilters]
  );

  const handleBackToRedView = useCallback(() => {
    setFilters({ nivel: 'red', cdp_id: '' });
  }, [setFilters]);

  const handleReset = useCallback(() => {
    if (isSupervisor) {
      setFilters({
        nivel: 'red',
        periodo: 'semana',
        red_id: supervisorRedId,
        cdp_id: '',
        q: '',
      });
    } else {
      resetFilters();
    }
  }, [isSupervisor, supervisorRedId, resetFilters, setFilters]);

  const supervisorSinRed = Boolean(
    isSupervisor &&
      (metricas?.sin_red_asignada || (metricas && Object.keys(metricas).length === 0 && !isLoading))
  );

  const hasData =
    nivel === 'general'
      ? Boolean(metricas?.total_casas && metricas.total_casas > 0)
      : nivel === 'red'
      ? Boolean(
          (metricas?.casas && metricas.casas.length > 0) ||
            (metricas?.casas_activas && metricas.casas_activas > 0)
        )
      : Boolean(metricas?.historial && metricas.historial.length > 0);

  return {
    user,
    isSupervisor,
    redes,
    filteredCasas,
    nivel,
    periodo,
    redId,
    cdpId,
    searchQuery,
    metricas,
    isLoading,
    isError,
    error,
    refetch,
    supervisorSinRed,
    hasData,
    handleNivelChange,
    handleRedChange,
    handleCdpChange,
    handleSearchChange,
    handlePeriodoChange,
    handleSelectRedFromRanking,
    handleBackToRedView,
    handleReset,
  };
}
