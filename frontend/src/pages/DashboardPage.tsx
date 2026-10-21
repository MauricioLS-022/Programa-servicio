import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useDashboard, useRedes } from '../hooks/useDashboard';
import { Card } from '../components/ui/Card';
import {
  Users,
  DollarSign,
  TrendingUp,
  HeartHandshake,
  Calendar,
  Layers,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [periodo, setPeriodo] = useState<'semana' | 'mes' | 'anio'>('semana');
  const [selectedRedId, setSelectedRedId] = useState<number | string>('');

  const { redes } = useRedes();
  const { metricas, isLoading } = useDashboard({
    nivel: user?.rol === 'admin' ? (selectedRedId ? 'red' : 'general') : 'red',
    red_id: selectedRedId || undefined,
    periodo,
  });

  const kpis = metricas?.kpis || {};
  const grafico = metricas?.grafico;
  const rankingRedes = metricas?.ranking_redes || [];

  return (
    <div className="flex flex-col gap-8">
      {/* Top Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-text-main dark:text-neutral-100 tracking-tight">
            Panel de Indicadores
          </h1>
          <p className="text-xs sm:text-sm text-text-muted dark:text-neutral-400 mt-1">
            Resumen ministerial de asistencia, fruto y ofrendas
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Admin Red Selector */}
          {user?.rol === 'admin' && (
            <select
              value={selectedRedId}
              onChange={(e) => setSelectedRedId(e.target.value)}
              className="rounded-lg border border-border-subtle dark:border-neutral-700 bg-white dark:bg-neutral-800 text-xs font-semibold py-2 px-3 text-text-main dark:text-neutral-200 outline-none focus:ring-2 focus:ring-vino/30 cursor-pointer"
            >
              <option value="">Todas las Redes (General)</option>
              {redes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.nombre}
                </option>
              ))}
            </select>
          )}

          {/* Dynamic Period Selector */}
          <div className="flex items-center p-1 rounded-xl bg-surface-sidebar dark:bg-neutral-800 border border-border-subtle dark:border-neutral-700">
            {(['semana', 'mes', 'anio'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPeriodo(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all cursor-pointer ${
                  periodo === p
                    ? 'bg-vino text-white shadow-xs dark:bg-vino'
                    : 'text-text-muted dark:text-neutral-400 hover:text-text-main dark:hover:text-neutral-200'
                }`}
              >
                {p === 'anio' ? 'Año' : p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
          <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
            Cargando indicadores ministeriales...
          </p>
        </div>
      ) : (
        <>
          {/* KPI Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <Card className="border-l-4 border-l-vino">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-400">
                    Asistencia Total
                  </p>
                  <p className="font-serif text-3xl font-extrabold text-text-main dark:text-neutral-100 mt-1">
                    {kpis.total_asistencia ?? 0}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-vino/10 text-vino dark:bg-vino/20 dark:text-vino-light">
                  <Users className="w-6 h-6" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between text-xs text-text-muted dark:text-neutral-400">
                <span>Promedio por reunión:</span>
                <span className="font-bold text-text-main dark:text-neutral-200">
                  {kpis.promedio_asistencia ?? 0}
                </span>
              </div>
            </Card>

            <Card className="border-l-4 border-l-emerald-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-400">
                    Ofrendas USD
                  </p>
                  <p className="font-serif text-3xl font-extrabold text-emerald-700 dark:text-emerald-400 mt-1">
                    ${(kpis.total_ofrenda_usd ?? 0).toFixed(2)}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400">
                  <DollarSign className="w-6 h-6" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between text-xs text-text-muted dark:text-neutral-400">
                <span>Total en Bolívares:</span>
                <span className="font-bold text-text-main dark:text-neutral-200">
                  Bs {(kpis.total_ofrenda_bs ?? 0).toLocaleString('es-VE', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </Card>

            <Card className="border-l-4 border-l-blue-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-400">
                    Nuevas Visitas
                  </p>
                  <p className="font-serif text-3xl font-extrabold text-text-main dark:text-neutral-100 mt-1">
                    {kpis.total_amigos ?? 0}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400">
                  <HeartHandshake className="w-6 h-6" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between text-xs text-text-muted dark:text-neutral-400">
                <span>Hermanos activos:</span>
                <span className="font-bold text-text-main dark:text-neutral-200">
                  {kpis.total_hermanos ?? 0}
                </span>
              </div>
            </Card>

            <Card className="border-l-4 border-l-amber-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-text-muted dark:text-neutral-400">
                    Niños Atendidos
                  </p>
                  <p className="font-serif text-3xl font-extrabold text-text-main dark:text-neutral-100 mt-1">
                    {kpis.total_ninos ?? 0}
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400">
                  <TrendingUp className="w-6 h-6" />
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between text-xs text-text-muted dark:text-neutral-400">
                <span>Período evaluado:</span>
                <span className="font-bold capitalize text-text-main dark:text-neutral-200">
                  {periodo}
                </span>
              </div>
            </Card>
          </div>

          {/* Chart & Secondary Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Interactive Bar Chart Representation */}
            <Card
              className="lg:col-span-2"
              title={`Tendencia de Asistencia (${periodo.toUpperCase()})`}
              subtitle="Comportamiento histórico y registro de reuniones"
              icon={<Calendar className="w-5 h-5" />}
            >
              {grafico?.asistencia && grafico.asistencia.length > 0 ? (
                <div className="flex flex-col gap-4">
                  <div className="h-64 flex items-end gap-3 sm:gap-6 pt-6 pb-2 px-2 overflow-x-auto scroll-containment">
                    {grafico.asistencia.map((val, idx) => {
                      const maxVal = Math.max(...grafico.asistencia!, 1);
                      const heightPercent = Math.round((val / maxVal) * 100);
                      const label = grafico.labels?.[idx] || `P${idx + 1}`;
                      const rango = grafico.fechas_rango?.[idx] || '';

                      return (
                        <div
                          key={idx}
                          className="flex-1 min-w-[3rem] flex flex-col items-center gap-2 group relative cursor-pointer"
                        >
                          {/* Tooltip */}
                          <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-900 text-white text-[11px] font-semibold py-1 px-2 rounded shadow-md pointer-events-none whitespace-nowrap z-20">
                            {val} asistentes {rango ? `(${rango})` : ''}
                          </div>

                          {/* Bar */}
                          <div className="w-full bg-surface-container dark:bg-neutral-700 rounded-t-lg h-44 flex items-end justify-center overflow-hidden">
                            <div
                              style={{ height: `${Math.max(heightPercent, 4)}%` }}
                              className="w-full bg-vino group-hover:bg-vino-hover transition-all rounded-t-lg"
                            />
                          </div>

                          <span className="text-[11px] font-bold text-text-muted dark:text-neutral-400 truncate max-w-[4rem]">
                            {label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="h-64 flex flex-col items-center justify-center text-text-muted dark:text-neutral-400 text-sm">
                  No hay reportes registrados para el período seleccionado.
                </div>
              )}
            </Card>

            {/* Network Ranking / Activity */}
            <Card
              title="Redes Ministeriales"
              subtitle="Rendimiento consolidado"
              icon={<Layers className="w-5 h-5" />}
              footer={
                <Link
                  to="/estructura"
                  className="text-xs font-bold text-vino dark:text-vino-light hover:underline flex items-center justify-between"
                >
                  <span>Explorar Estructura Ministerial</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              }
            >
              <div className="flex flex-col gap-3 max-h-64 overflow-y-auto scroll-containment pr-1">
                {rankingRedes.length > 0 ? (
                  rankingRedes.map((red, index) => (
                    <div
                      key={red.red_id || index}
                      className="flex items-center justify-between p-3 rounded-xl bg-surface-low/60 dark:bg-neutral-800/60 border border-border-subtle/60 dark:border-neutral-700/60"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-vino/10 dark:bg-vino/30 text-vino dark:text-vino-light text-xs font-bold flex items-center justify-center">
                          {index + 1}
                        </span>
                        <span className="text-xs font-bold text-text-main dark:text-neutral-200">
                          {red.nombre}
                        </span>
                      </div>
                      <span className="text-xs font-extrabold text-vino dark:text-vino-light">
                        {red.asistencia} asistentes
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-text-muted dark:text-neutral-400 py-6 text-center">
                    Cargando información ministerial...
                  </p>
                )}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

