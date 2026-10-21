import React, { useState, useMemo } from 'react';
import { useRedes, useCasasDePaz } from '../hooks/useDashboard';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import {
  Search,
  Phone,
  MessageCircle,
  MapPin,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2,
} from 'lucide-react';

export const EstructuraPage: React.FC = () => {
  const [selectedRedId, setSelectedRedId] = useState<number | string>('');
  const [filtroEstado, setFiltroEstado] = useState<'todas' | 'pendientes_7d' | 'activas'>('todas');
  const [search, setSearch] = useState('');

  const { redes } = useRedes();
  const { casas, isLoading } = useCasasDePaz({
    red_id: selectedRedId || undefined,
  });

  // Client-Side Live Search & Filtering (Paridad con estructura.js)
  const filteredCasas = useMemo(() => {
    return casas.filter((c) => {
      const matchSearch =
        search === '' ||
        c.codigo?.toLowerCase().includes(search.toLowerCase()) ||
        c.anfitrion?.toLowerCase().includes(search.toLowerCase()) ||
        c.direccion?.toLowerCase().includes(search.toLowerCase());

      let matchEstado = true;
      if (filtroEstado === 'pendientes_7d') {
        matchEstado = Boolean(c.sin_reporte_7d);
      } else if (filtroEstado === 'activas') {
        matchEstado = Boolean(c.is_active);
      }

      return matchSearch && matchEstado;
    });
  }, [casas, search, filtroEstado]);

  const pendientesCount = useMemo(() => {
    return casas.filter((c) => c.sin_reporte_7d).length;
  }, [casas]);

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-text-main dark:text-neutral-100 tracking-tight">
            Estructura Ministerial
          </h1>
          <p className="text-xs sm:text-sm text-text-muted dark:text-neutral-400 mt-1">
            Redes de discipulado y Casas de Paz ({casas.length} casas registradas)
          </p>
        </div>

        {/* 7-Day Alert Banner Pill */}
        {pendientesCount > 0 && (
          <div className="inline-flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 text-amber-900 dark:text-amber-300 text-xs font-semibold">
            <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>
              {pendientesCount} {pendientesCount === 1 ? 'casa pendiente' : 'casas pendientes'} de reporte esta semana
            </span>
          </div>
        )}
      </div>

      {/* Network Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto scroll-containment pb-2">
        <button
          onClick={() => setSelectedRedId('')}
          className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
            selectedRedId === ''
              ? 'bg-vino text-white shadow-xs'
              : 'bg-white dark:bg-neutral-800 text-text-muted dark:text-neutral-400 hover:text-text-main dark:hover:text-neutral-200 border border-border-subtle dark:border-neutral-700'
          }`}
        >
          Todas las Redes
        </button>
        {redes.map((r) => (
          <button
            key={r.id}
            onClick={() => setSelectedRedId(r.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
              selectedRedId === r.id
                ? 'bg-vino text-white shadow-xs'
                : 'bg-white dark:bg-neutral-800 text-text-muted dark:text-neutral-400 hover:text-text-main dark:hover:text-neutral-200 border border-border-subtle dark:border-neutral-700'
            }`}
          >
            {r.nombre} {r.supervisor_nombre ? `(${r.supervisor_nombre})` : ''}
          </button>
        ))}
      </div>

      {/* Live Search and Quick Filter Bar */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <Input
              id="casasSearchInput"
              placeholder="Buscar por código, anfitrión, líder o dirección..."
              icon={<Search className="w-4 h-4" />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-sidebar dark:bg-neutral-800 border border-border-subtle dark:border-neutral-700 self-start sm:self-auto">
            <button
              onClick={() => setFiltroEstado('todas')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                filtroEstado === 'todas'
                  ? 'bg-vino text-white shadow-xs'
                  : 'text-text-muted dark:text-neutral-400'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setFiltroEstado('pendientes_7d')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                filtroEstado === 'pendientes_7d'
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'text-text-muted dark:text-neutral-400'
              }`}
            >
              Sin Reporte (7d)
            </button>
            <button
              onClick={() => setFiltroEstado('activas')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                filtroEstado === 'activas'
                  ? 'bg-vino text-white shadow-xs'
                  : 'text-text-muted dark:text-neutral-400'
              }`}
            >
              Activas
            </button>
          </div>
        </div>
      </Card>

      {/* Grid of Casas de Paz Cards */}
      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
          <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
            Cargando estructura de Casas de Paz...
          </p>
        </div>
      ) : filteredCasas.length === 0 ? (
        <div className="py-16 text-center text-text-muted dark:text-neutral-400 text-sm">
          No se encontraron Casas de Paz que coincidan con la búsqueda.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCasas.map((casa) => {
            const cleanPhone = (casa.telefono || '').replace(/[^0-9]/g, '');

            return (
              <Card
                key={casa.id}
                className="hover:border-vino/50 transition-all flex flex-col justify-between"
              >
                <div>
                  {/* Top Badge & Code */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="font-serif text-lg font-bold text-text-main dark:text-neutral-100">
                      {casa.codigo}
                    </span>

                    {casa.sin_reporte_7d ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                        <AlertCircle className="w-3 h-3 text-amber-600" />
                        Sin Reporte 7d
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300">
                        <CheckCircle className="w-3 h-3 text-emerald-600" />
                        Al Día
                      </span>
                    )}
                  </div>

                  {/* Anfitrión & Red */}
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-text-main dark:text-neutral-200">
                      Anfitrión: {casa.anfitrion || 'Por asignar'}
                    </p>
                    <p className="text-[11px] text-text-muted dark:text-neutral-400 mt-0.5">
                      {casa.red_nombre || 'Red Ministerial'}
                    </p>
                  </div>

                  {/* Horario y Ubicación */}
                  <div className="flex flex-col gap-2 text-xs text-text-muted dark:text-neutral-400 py-3 border-t border-border-subtle/60 dark:border-neutral-700/60">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 shrink-0 text-vino dark:text-vino-light" />
                      <span>
                        {casa.dia_semana || 'Día por definir'} • {casa.hora || 'Horario flexible'}
                      </span>
                    </div>
                    {casa.direccion && (
                      <div className="flex items-start gap-2">
                        <MapPin className="w-3.5 h-3.5 shrink-0 text-vino dark:text-vino-light mt-0.5" />
                        <span className="truncate">{casa.direccion}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer with direct WhatsApp and Call links */}
                <div className="mt-4 pt-3 border-t border-border-subtle/60 dark:border-neutral-700/60 flex items-center justify-between gap-2">
                  <span className="text-[11px] font-medium text-text-muted dark:text-neutral-400">
                    {casa.total_lideres ? `${casa.total_lideres} líderes` : '1 líder asignado'}
                  </span>

                  <div className="flex items-center gap-2">
                    {casa.telefono && (
                      <>
                        <a
                          href={`tel:${cleanPhone}`}
                          className="p-1.5 rounded-lg text-text-muted hover:text-text-main hover:bg-surface-low dark:hover:bg-neutral-700 transition-colors"
                          title="Llamar por teléfono"
                        >
                          <Phone className="w-4 h-4" />
                        </a>
                        <a
                          href={`https://wa.me/${cleanPhone}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-lg text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 transition-colors"
                          title="Enviar WhatsApp directo"
                        >
                          <MessageCircle className="w-4 h-4" />
                        </a>
                      </>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
