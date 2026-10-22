import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDashboard, useRedes, useCasasDePaz } from '../hooks/useDashboard';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { DashboardEmptyState } from '../components/dashboard/DashboardEmptyState';
import { DashboardPeriodToggle, type PeriodoTipo } from '../components/dashboard/DashboardPeriodToggle';
import { DashboardFilterBar } from '../components/dashboard/DashboardFilterBar';
import { DashboardKpiCards } from '../components/dashboard/DashboardKpiCards';
import { DashboardTrendChart } from '../components/dashboard/DashboardTrendChart';
import { DashboardCategoryDonut } from '../components/dashboard/DashboardCategoryDonut';
import { DashboardAlertsCard } from '../components/dashboard/DashboardAlertsCard';
import { DashboardRankingCard } from '../components/dashboard/DashboardRankingCard';
import { DashboardFrutoCard } from '../components/dashboard/DashboardFrutoCard';
import { DashboardRedDetail } from '../components/dashboard/DashboardRedDetail';
import { DashboardCdpDetail } from '../components/dashboard/DashboardCdpDetail';
import { Loader2, RefreshCw } from 'lucide-react';
import '../styles/dashboard.css';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const isSupervisor = user?.rol === 'supervisor';

  // Estados de control jerárquico
  const [periodo, setPeriodo] = useState<PeriodoTipo>('semana');
  const [nivel, setNivel] = useState<'general' | 'red' | 'cdp'>(isSupervisor ? 'red' : 'general');
  const [redId, setRedId] = useState<number | string>('');
  const [cdpId, setCdpId] = useState<number | string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Carga de selectores y métricas del dashboard
  const { redes } = useRedes();
  const { casas: allCasas } = useCasasDePaz();
  const { metricas, isLoading, isError, error, refetch } = useDashboard({
    nivel,
    red_id: redId || undefined,
    cdp_id: cdpId || undefined,
    periodo,
  });

  // Filtrado reactivo de Casas de Paz por búsqueda rápida
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

  // Auto-selección reactiva de Red y Casa de Paz al conmutar niveles
  React.useEffect(() => {
    if (nivel === 'red') {
      if (!redId && redes.length > 0) {
        setRedId(redes[0].id);
      }
    } else if (nivel === 'cdp') {
      const activeRed = redId || (redes.length > 0 ? redes[0].id : '');
      if (!redId && activeRed) {
        setRedId(activeRed);
      }
      if (!cdpId && allCasas.length > 0) {
        const candidateCasas = activeRed
          ? allCasas.filter((c) => c.red_id === Number(activeRed))
          : allCasas;
        if (candidateCasas.length > 0) {
          setCdpId(candidateCasas[0].id);
        } else if (allCasas.length > 0) {
          setCdpId(allCasas[0].id);
        }
      }
    }
  }, [nivel, redId, cdpId, redes, allCasas]);

  // Manejo de reinicio de filtros
  const handleReset = () => {
    setSearchQuery('');
    setPeriodo('semana');
    setNivel(isSupervisor ? 'red' : 'general');
    setRedId('');
    setCdpId('');
  };

  // Validación de estado de supervisor sin red asignada
  const supervisorSinRed = isSupervisor && (metricas?.sin_red_asignada || (metricas && Object.keys(metricas).length === 0 && !isLoading));

  return (
    <div className="dashboard-admin-wrapper">
      <main className="dashboard-main">
        {/* Cabecera dinámica de sección */}
        <DashboardHeader
          rol={user?.rol}
          userName={user?.nombre || user?.username || 'Usuario'}
          nivel={nivel}
          redNombre={metricas?.nombre_red}
          supervisorNombre={metricas?.supervisor}
          casasActivas={metricas?.casas_activas}
          cdpNombre={metricas?.nombre_cdp}
          cdpDireccion={metricas?.direccion}
        />

        {/* Estado vacío: Supervisor sin red ministerial asignada */}
        {supervisorSinRed ? (
          <DashboardEmptyState type="sin_red" />
        ) : (
          <>
            {/* Barra de Filtros Jerárquicos y Búsqueda */}
            <DashboardFilterBar
              rol={user?.rol}
              nivel={nivel}
              onNivelChange={(newNivel) => {
                setNivel(newNivel);
                if (newNivel === 'general') {
                  setRedId('');
                  setCdpId('');
                } else if (newNivel === 'red') {
                  setCdpId('');
                  if (!redId && redes.length > 0) {
                    setRedId(redes[0].id);
                  }
                } else if (newNivel === 'cdp') {
                  const activeRed = redId || (redes.length > 0 ? redes[0].id : '');
                  if (!redId && activeRed) {
                    setRedId(activeRed);
                  }
                  const candidateCasas = activeRed
                    ? allCasas.filter((c) => c.red_id === Number(activeRed))
                    : allCasas;
                  if (candidateCasas.length > 0) {
                    setCdpId(candidateCasas[0].id);
                  } else if (allCasas.length > 0) {
                    setCdpId(allCasas[0].id);
                  }
                }
              }}
              redId={redId}
              onRedChange={(newRedId) => {
                setRedId(newRedId);
                if (nivel === 'cdp' && newRedId) {
                  const candidateCasas = allCasas.filter((c) => c.red_id === Number(newRedId));
                  if (candidateCasas.length > 0) {
                    setCdpId(candidateCasas[0].id);
                  } else {
                    setCdpId('');
                  }
                } else {
                  setCdpId('');
                }
              }}
              redes={redes}
              cdpId={cdpId}
              onCdpChange={(newCdpId) => setCdpId(newCdpId)}
              casas={filteredCasas}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              onReset={handleReset}
            />

            {/* Barra de Accesos Rápidos y Selector de Período Dinámico */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '1rem',
                marginBottom: '1.25rem',
              }}
            >
              {/* Botones de navegación directa institucional */}
              <div className="quick-actions-bar fade-in-1" style={{ margin: 0 }}>
                <Link to="/reportes" className="quick-action-btn">
                  <span className="material-symbols-outlined">table_chart</span>
                  <span>Ver Reportes</span>
                </Link>
                <Link to="/estructura" className="quick-action-btn">
                  <span className="material-symbols-outlined">account_tree</span>
                  <span>Estructura y Redes</span>
                </Link>
                <Link to="/lideres" className="quick-action-btn">
                  <span className="material-symbols-outlined">group</span>
                  <span>Directorio de Líderes</span>
                </Link>
              </div>

              {/* Selector táctil de período temporal */}
              <DashboardPeriodToggle
                periodo={periodo}
                onChange={setPeriodo}
                disabled={isLoading}
              />
            </div>

            {/* Estado de Carga / Error */}
            {isLoading && (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '4rem 1rem',
                  gap: '0.75rem',
                }}
              >
                <Loader2
                  className="animate-spin text-vino"
                  style={{ width: '2.5rem', height: '2.5rem' }}
                />
                <p style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.95rem', fontWeight: 600 }}>
                  Actualizando métricas ministeriales...
                </p>
              </div>
            )}

            {isError && (
              <div
                className="warning-card"
                style={{
                  padding: '2rem',
                  textAlign: 'center',
                  margin: '1.5rem 0',
                }}
              >
                <span
                  className="material-symbols-outlined text-danger"
                  style={{ fontSize: '2.5rem', marginBottom: '0.5rem', display: 'block' }}
                >
                  error
                </span>
                <h3 style={{ color: 'var(--primary, #390002)', marginBottom: '0.5rem' }}>
                  No se pudieron cargar los datos del dashboard
                </h3>
                <p style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                  {(error as Error)?.message || 'Ocurrió un error consultando el servidor.'}
                </p>
                <button
                  type="button"
                  onClick={() => refetch()}
                  className="quick-action-btn"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', margin: '0 auto' }}
                >
                  <RefreshCw style={{ width: '1rem', height: '1rem' }} />
                  Reintentar
                </button>
              </div>
            )}

            {!isLoading && !isError && (
              <>
                {/* Grid Superior de Tarjetas KPI */}
                <DashboardKpiCards
                  metricas={metricas}
                  nivel={nivel}
                  periodo={periodo}
                  hasData={Boolean(metricas && Object.keys(metricas).length > 0)}
                />

                {/* Grid Principal de 2 Columnas */}
                <div className="dashboard-grid">
                  {/* Columna Izquierda: Gráficas de Tendencia, Distribución y Detalle Zonal */}
                  <div className="main-column">
                    {/* Gráfico de barras de evolución temporal reactiva */}
                    <DashboardTrendChart
                      tendencia={metricas?.tendencia_semanas || metricas?.tendencia}
                      promedioTendencia={metricas?.promedio_tendencia}
                      periodo={periodo}
                      periodoNombre={metricas?.periodo_nombre}
                      nivel={nivel}
                      redNombre={metricas?.nombre_red}
                    />

                    {/* Gráfico Donut de distribución por categoría */}
                    <DashboardCategoryDonut
                      distribucion={metricas?.distribucion}
                      total={metricas?.total_asistencia ?? metricas?.asistencia_total}
                      periodo={periodo}
                      periodoNombre={metricas?.periodo_nombre}
                      nivel={nivel}
                      redNombre={metricas?.nombre_red}
                    />

                    {/* Vista de Detalle Zonal de Casas de Paz cuando el filtro es Red */}
                    {nivel === 'red' && (
                      <DashboardRedDetail
                        redNombre={metricas?.nombre_red}
                        casas={metricas?.casas}
                        actividadReciente={metricas?.actividad_reciente}
                        lideresRed={metricas?.lideres_red}
                        topCrecimiento={metricas?.top_crecimiento}
                        cumplimiento={metricas?.cumplimiento}
                        casasConReporte={metricas?.casas_con_reporte}
                        casasPendientes={metricas?.casas_pendientes}
                        casasActivas={metricas?.casas_activas}
                        periodo={periodo}
                        periodoNombre={metricas?.periodo_nombre}
                        onSelectCdp={(selectedId) => {
                          setNivel('cdp');
                          setCdpId(selectedId);
                        }}
                      />
                    )}
                    {/* Vista de Detalle de Casa de Paz cuando el filtro es CDP */}
                    {nivel === 'cdp' && (
                      <DashboardCdpDetail
                        metricas={metricas}
                        periodo={periodo}
                        periodoNombre={metricas?.periodo_nombre}
                      />
                    )}
                  </div>

                  {/* Columna Derecha (Sidebar): Alertas, Ranking y Fruto */}
                  <aside className="sidebar-column fade-in-6">
                    {/* Alertas de Seguimiento (>2 semanas sin reporte con contacto directo) */}
                    {nivel !== 'cdp' && (
                      <DashboardAlertsCard
                        alertas={nivel === 'red' ? metricas?.alertas_zonal || metricas?.alertas : metricas?.alertas}
                        isZonal={nivel === 'red'}
                        title={nivel === 'red' ? 'Alertas de la Red' : 'Alertas de Seguimiento'}
                      />
                    )}

                    {/* Podio y Ranking de Redes (Visible en Vista General) */}
                    {nivel === 'general' && (
                      <DashboardRankingCard
                        ranking={metricas?.ranking_redes}
                        periodo={periodo}
                        periodoNombre={metricas?.periodo_nombre}
                      />
                    )}

                    {/* Fruto y Transformación Espiritual */}
                    <DashboardFrutoCard
                      conversiones={metricas?.conversiones}
                      reconciliaciones={metricas?.reconciliaciones}
                      cestasAmor={metricas?.cestas_amor}
                      totalVisitas={metricas?.total_visitas}
                    />
                  </aside>
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
};
