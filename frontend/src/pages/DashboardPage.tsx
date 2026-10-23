import React, { useState, useMemo, useEffect } from 'react';
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
import { DashboardRecentActivity } from '../components/dashboard/DashboardRecentActivity';
import { DashboardRedSidebar } from '../components/dashboard/DashboardRedSidebar';
import { DashboardCdpFicha } from '../components/dashboard/DashboardCdpFicha';
import { DashboardCdpHistoryTable } from '../components/dashboard/DashboardCdpHistoryTable';
import { DashboardCdpSidebar } from '../components/dashboard/DashboardCdpSidebar';
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

  // Auto-selección y aislamiento estricto de Red y Casa de Paz al conmutar niveles
  useEffect(() => {
    if (nivel === 'red') {
      setCdpId('');
      if (!redId && redes.length > 0) {
        setRedId(redes[0].id);
      }
    } else if (nivel === 'cdp') {
      const activeRed = redId || (redes.length > 0 ? redes[0].id : '');
      if (!redId && activeRed) {
        setRedId(activeRed);
      }
      const candidateCasas = activeRed
        ? allCasas.filter((c) => c.red_id === Number(activeRed))
        : allCasas;

      // Verificar si cdpId actual pertenece a las casas de esta red
      const currentValid = candidateCasas.some((c) => String(c.id) === String(cdpId));
      if (!currentValid) {
        if (candidateCasas.length > 0) {
          setCdpId(candidateCasas[0].id);
        } else {
          setCdpId(''); // Si la red no tiene casas, dejar cdpId vacío para activar estado vacío
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

  // Evaluación de presencia de datos según nivel (paridad Jinja)
  const hasData =
    nivel === 'general'
      ? Boolean(metricas?.total_casas && metricas.total_casas > 0)
      : nivel === 'red'
      ? Boolean((metricas?.casas && metricas.casas.length > 0) || (metricas?.casas_activas && metricas.casas_activas > 0))
      : Boolean(metricas?.historial && metricas.historial.length > 0);

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
                  } else {
                    setCdpId('');
                  }
                }
              }}
              redId={redId}
              onRedChange={(newRedId) => {
                setRedId(newRedId);
                if (nivel === 'cdp') {
                  if (newRedId) {
                    const candidateCasas = allCasas.filter((c) => c.red_id === Number(newRedId));
                    if (candidateCasas.length > 0) {
                      setCdpId(candidateCasas[0].id);
                    } else {
                      setCdpId('');
                    }
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

            {/* Estado de Carga */}
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

            {/* Estado de Error */}
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
                {/* ===================================================================
                     VISTA 1: GENERAL (IGLESIA GLOBAL)
                     =================================================================== */}
                {nivel === 'general' && (
                  <>
                    <DashboardKpiCards
                      metricas={metricas}
                      nivel="general"
                      periodo={periodo}
                      hasData={hasData}
                    />

                    <div className="dashboard-grid">
                      {/* Columna Izquierda: Tendencia y Donut a Ancho Completo */}
                      <div className="main-column">
                        <DashboardTrendChart
                          tendencia={metricas?.tendencia_semanas || metricas?.tendencia}
                          promedioTendencia={metricas?.promedio_tendencia}
                          periodo={periodo}
                          periodoNombre={metricas?.periodo_nombre}
                          nivel="general"
                          redNombre={metricas?.nombre_red}
                        />

                        <div style={{ marginTop: '1rem' }}>
                          <DashboardCategoryDonut
                            distribucion={metricas?.distribucion}
                            total={metricas?.total_asistencia ?? metricas?.asistencia_total}
                            periodo={periodo}
                            periodoNombre={metricas?.periodo_nombre}
                            nivel="general"
                            redNombre={metricas?.nombre_red}
                          />
                        </div>
                      </div>

                      {/* Columna Derecha (Sidebar General): Alertas, Ranking y Fruto */}
                      <aside className="sidebar-column fade-in-6">
                        <DashboardAlertsCard
                          alertas={metricas?.alertas}
                          isZonal={false}
                          title="Alertas de Seguimiento"
                        />

                        <DashboardRankingCard
                          ranking={metricas?.ranking_redes}
                          periodo={periodo}
                          periodoNombre={metricas?.periodo_nombre}
                        />

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

                {/* ===================================================================
                     VISTA 2: RED / ZONAL
                     =================================================================== */}
                {nivel === 'red' && (
                  <>
                    <DashboardKpiCards
                      metricas={metricas}
                      nivel="red"
                      periodo={periodo}
                      hasData={hasData}
                    />

                    <div className="dashboard-grid">
                      {/* Columna Izquierda: Tendencia, Actividad Reciente y Donut Zonal */}
                      <div className="main-column">
                        <DashboardTrendChart
                          tendencia={metricas?.tendencia_semanas || metricas?.tendencia}
                          promedioTendencia={metricas?.promedio_tendencia}
                          periodo={periodo}
                          periodoNombre={metricas?.periodo_nombre}
                          nivel="red"
                          redNombre={metricas?.nombre_red}
                        />

                        <DashboardRecentActivity
                          redNombre={metricas?.nombre_red}
                          actividadReciente={metricas?.actividad_reciente}
                        />

                        <div style={{ marginTop: '1rem' }}>
                          <DashboardCategoryDonut
                            distribucion={metricas?.distribucion}
                            total={metricas?.total_asistencia ?? metricas?.asistencia_total}
                            periodo={periodo}
                            periodoNombre={metricas?.periodo_nombre}
                            nivel="red"
                            redNombre={metricas?.nombre_red}
                          />
                        </div>
                      </div>

                      {/* Columna Derecha (Sidebar Red): Alertas Zonal, Top Crecimiento, Cumplimiento y Líderes */}
                      <DashboardRedSidebar
                        redNombre={metricas?.nombre_red}
                        alertas={metricas?.alertas_zonal || metricas?.alertas}
                        topCrecimiento={metricas?.top_crecimiento}
                        cumplimiento={metricas?.cumplimiento}
                        casasConReporte={metricas?.casas_con_reporte}
                        casasPendientes={metricas?.casas_pendientes}
                        casasActivas={metricas?.casas_activas}
                        periodo={periodo}
                        periodoNombre={metricas?.periodo_nombre}
                        lideresRed={metricas?.lideres_red}
                      />
                    </div>
                  </>
                )}

                {/* ===================================================================
                     VISTA 3: CASA DE PAZ
                     =================================================================== */}
                {nivel === 'cdp' && (
                  <>
                    {!cdpId ? (
                      /* Estado vacío: La red no tiene Casas de Paz asignadas */
                      <section
                        className="empty-state-card fade-in-1"
                        style={{
                          margin: '2rem auto',
                          maxWidth: '640px',
                          textAlign: 'center',
                          padding: '3.5rem 2rem',
                          background: 'var(--color4, #fff)',
                          borderRadius: '12px',
                          boxShadow: 'var(--shadow-card, 0 4px 20px rgba(35,25,25,0.04))',
                          border: '1px solid rgba(137, 114, 111, 0.15)',
                        }}
                      >
                        <span
                          className="material-symbols-outlined"
                          style={{ fontSize: '3.8rem', color: 'var(--color5, #96292b)', marginBottom: '1rem' }}
                        >
                          home_work
                        </span>
                        <h2
                          style={{
                            fontFamily: "var(--font-serif, 'Noto Serif', serif)",
                            color: 'var(--primary, #390002)',
                            marginBottom: '0.75rem',
                            fontSize: '1.5rem',
                          }}
                        >
                          Sin Casas de Paz Asignadas
                        </h2>
                        <p style={{ color: '#64748b', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
                          La red seleccionada{' '}
                          {metricas?.nombre_red && <strong>({metricas.nombre_red}) </strong>}
                          aún no tiene Casas de Paz registradas o activas. Puedes seleccionar otra red en el filtro superior o registrar nuevas Casas de Paz desde la sección de Estructura.
                        </p>
                        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                          <button
                            type="button"
                            onClick={() => setNivel('red')}
                            className="btn-full-outline"
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                              padding: '0.55rem 1.15rem',
                              borderRadius: '8px',
                              fontWeight: 600,
                              fontSize: '0.9rem',
                              cursor: 'pointer',
                            }}
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: '1.1rem' }}>
                              arrow_back
                            </span>
                            Ver Vista Zonal
                          </button>
                          <Link
                            to="/estructura"
                            className="btn-full-primary"
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                              textDecoration: 'none',
                              padding: '0.55rem 1.15rem',
                              borderRadius: '8px',
                              fontWeight: 600,
                              fontSize: '0.9rem',
                              background: 'var(--primary, #780204)',
                              color: '#fff',
                            }}
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: '1.1rem' }}>
                              account_tree
                            </span>
                            Estructura y Redes
                          </Link>
                        </div>
                      </section>
                    ) : (
                      <>
                        {/* Ficha del Líder & Trazabilidad Superior */}
                        <DashboardCdpFicha metricas={metricas} />

                        {/* 4 KPIs de Casa de Paz */}
                        <div style={{ marginTop: '1.25rem' }}>
                          <DashboardKpiCards
                            metricas={metricas}
                            nivel="cdp"
                            periodo={periodo}
                            hasData={hasData}
                          />
                        </div>

                        {/* Grilla Principal de 2 Columnas de Casa de Paz */}
                        <div className="dashboard-grid">
                          {/* Columna Izquierda: Historial de Reportes y Donut del Último Reporte */}
                          <div className="main-column">
                            <DashboardCdpHistoryTable historial={metricas?.historial} />

                            <div style={{ marginTop: '1rem' }}>
                              <DashboardCategoryDonut
                                distribucion={metricas?.distribucion}
                                total={metricas?.asistencia_ultimo}
                                periodo={periodo}
                                periodoNombre={metricas?.periodo_nombre}
                                nivel="cdp"
                                redNombre={metricas?.nombre_red}
                              />
                            </div>
                          </div>

                          {/* Columna Derecha (Sidebar CDP): Notas, Dinámica, Mini Histórico y Anfitrión */}
                          <DashboardCdpSidebar metricas={metricas} />
                        </div>
                      </>
                    )}
                  </>
                )}
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
};

