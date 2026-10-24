import React, { useState, useMemo, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { useRedes, useCasasDePaz } from '../hooks/useDashboard';
import { useEstructuraMutations, useEstructuraSelectores } from '../hooks/useEstructura';
import { useAuth } from '../hooks/useAuth';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useUrlFilters } from '../hooks/useUrlFilters';
import { useToast } from '../context/ToastContext';
import { RedModal } from '../components/estructura/RedModal';
import { CasaDePazModal } from '../components/estructura/CasaDePazModal';
import { RedBottomSheet } from '../components/estructura/RedBottomSheet';
import { Icon } from '../components/ui/Icon';
import {
  Search,
  Plus,
  Network,
  Home,
  ArrowRight,
  MoreVertical,
  PauseCircle,
  PlayCircle,
  Edit,
  Trash2,
  Users,
  Shield,
  User,
  Calendar,
  BadgeCheck,
  Clock,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  X,
  Loader2,
} from 'lucide-react';
import type { Red, CasaDePaz, RedInput, CdpInput } from '../types/estructura';
import '../styles/estructura.css';

export const EstructuraPage: React.FC = () => {
  useDocumentTitle('Estructura');

  const { user } = useAuth();
  const { success, error } = useToast();
  const isAdmin = user?.rol === 'admin';
  const isSupervisor = user?.rol === 'supervisor';

  // Configuración de filtros por defecto (Ruta limpia canónica: /estructura)
  const defaultEstructuraFilters = useMemo(
    () => ({
      red_id: '',
      filtro: 'todas' as 'todas' | 'pendientes_7d' | 'activas',
      q: '',
    }),
    []
  );

  // Sincronización bidireccional con URLSearchParams como Fuente Única de la Verdad (SSOT)
  const { filters, setFilter, setFilters, searchParams } = useUrlFilters(
    defaultEstructuraFilters,
    { cleanupKeys: ['cdp_id', 'casa_id'] }
  );

  const selectedRedId = filters.red_id;
  const filtroEstado = filters.filtro;
  const search = filters.q;
  const initialCdpId = useMemo(
    () => searchParams.get('cdp_id') || searchParams.get('casa_id') || '',
    []
  );
  const [highlightedCdpId, setHighlightedCdpId] = useState<string | null>(initialCdpId || null);

  // Queries y Mutaciones
  const { redes, refetch: refetchRedes } = useRedes();
  const { casas, isLoading, refetch: refetchCasas } = useCasasDePaz();
  const { selectores } = useEstructuraSelectores();

  const {
    crearRed,
    isCreandoRed,
    editarRed,
    isEditandoRed,
    toggleRed,
    eliminarRed,
    isEliminandoRed,
    crearCdp,
    isCreandoCdp,
    editarCdp,
    isEditandoCdp,
    eliminarCdp,
    isEliminandoCdp,
  } = useEstructuraMutations();

  // Modales
  const [redModalData, setRedModalData] = useState<{ isOpen: boolean; red: Red | null }>({
    isOpen: false,
    red: null,
  });
  const [cdpModalData, setCdpModalData] = useState<{ isOpen: boolean; casa: CasaDePaz | null }>({
    isOpen: false,
    casa: null,
  });

  const [activeMenuRedId, setActiveMenuRedId] = useState<number | null>(null);
  const [activeMenuRed, setActiveMenuRed] = useState<Red | null>(null);
  const [menuPos, setMenuPos] = useState<{ top: number; right: number } | null>(null);
  const [isMobileSheetOpen, setIsMobileSheetOpen] = useState(false);

  // Toast flotante de notificación (una vez por sesión)
  const [showToast, setShowToast] = useState(() => {
    return !sessionStorage.getItem('reportes_toast_dismissed');
  });

  // Limpieza de nombres de red para evitar duplicación ("Red Red Hebrón" -> "Hebrón")
  const cleanRedName = (name?: string) => (name ? name.replace(/^Red\s+/i, '').trim() : '');

  // Referencias para flechas de scroll en mobile
  const sidebarRef = useRef<HTMLElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Detección de dispositivo táctil / teléfono para navegación por swipe nativo sin flechas
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  useEffect(() => {
    const checkTouch = () => {
      const hasTouch =
        typeof window !== 'undefined' &&
        ('ontouchstart' in window ||
          navigator.maxTouchPoints > 0 ||
          window.matchMedia('(pointer: coarse)').matches);
      setIsTouchDevice(Boolean(hasTouch));
    };
    checkTouch();
  }, []);

  const checkScrollArrows = () => {
    if (isTouchDevice || !sidebarRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = sidebarRef.current;
    const maxScroll = scrollWidth - clientWidth;
    if (maxScroll <= 10) {
      setCanScrollLeft(false);
      setCanScrollRight(false);
      return;
    }
    setCanScrollLeft(scrollLeft > 5);
    setCanScrollRight(scrollLeft < maxScroll - 5);
  };

  useEffect(() => {
    if (isTouchDevice) return;
    checkScrollArrows();
    const elem = sidebarRef.current;
    if (elem) {
      elem.addEventListener('scroll', checkScrollArrows);
      window.addEventListener('resize', checkScrollArrows);
      return () => {
        elem.removeEventListener('scroll', checkScrollArrows);
        window.removeEventListener('resize', checkScrollArrows);
      };
    }
  }, [redes, isTouchDevice]);

  const handleScrollSidebar = (direction: 'left' | 'right') => {
    if (!sidebarRef.current) return;
    const SCROLL_AMOUNT = 150;
    sidebarRef.current.scrollBy({
      left: direction === 'left' ? -SCROLL_AMOUNT : SCROLL_AMOUNT,
      behavior: 'smooth',
    });
  };

  // Efecto de Deep Linking: Desplazamiento Suave y Resaltado Temporal
  const hasScrolledRef = useRef(false);
  useEffect(() => {
    if (initialCdpId && !hasScrolledRef.current && casas.length > 0) {
      const targetElement = document.getElementById(`cdp-${initialCdpId}`);
      if (targetElement) {
        hasScrolledRef.current = true;
        setHighlightedCdpId(initialCdpId);
        setTimeout(() => {
          targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);

        const timer = setTimeout(() => {
          setHighlightedCdpId(null);
        }, 3500);
        return () => clearTimeout(timer);
      }
    }
  }, [initialCdpId, casas]);

  // Sincronizar selección de Red con la URL (elimina el parámetro si es "todas" o vacía)
  const handleSelectRed = (id: number | string) => {
    const redStr = String(id === 'all' || !id ? '' : id);
    setFilters({ red_id: redStr }, ['cdp_id', 'casa_id']);
  };

  // Sincronizar filtro de estado con la URL (elimina si es 'todas')
  const handleFiltroEstadoChange = (estado: 'todas' | 'pendientes_7d' | 'activas') => {
    setFilters({ filtro: estado }, ['cdp_id', 'casa_id']);
  };

  // Sincronizar búsqueda con la URL (elimina si está vacía)
  const handleSearchChange = (value: string) => {
    setFilters({ q: value }, ['cdp_id', 'casa_id']);
  };

  // Cerrar menú contextual si se hace click fuera, resize o scroll
  useEffect(() => {
    const handleClose = () => {
      setActiveMenuRedId(null);
      setActiveMenuRed(null);
      setMenuPos(null);
    };
    if (activeMenuRedId !== null) {
      document.addEventListener('click', handleClose);
      window.addEventListener('resize', handleClose);
      window.addEventListener('scroll', handleClose, true);
      return () => {
        document.removeEventListener('click', handleClose);
        window.removeEventListener('resize', handleClose);
        window.removeEventListener('scroll', handleClose, true);
      };
    }
  }, [activeMenuRedId]);

  // Nombre de la red actualmente seleccionada
  const selectedRedObj = useMemo(() => {
    if (!selectedRedId || selectedRedId === 'all') return null;
    return redes.find((r) => String(r.id) === String(selectedRedId));
  }, [redes, selectedRedId]);

  const selectedRedName = useMemo(() => {
    if (selectedRedObj) return `Red ${cleanRedName(selectedRedObj.nombre)}`;
    if (isSupervisor && redes.length > 0) return `Red ${cleanRedName(redes[0].nombre)}`;
    return 'todas las redes';
  }, [selectedRedObj, isSupervisor, redes]);

  // Filtrado reactivo de Casas de Paz (cliente, paridad canónica con estructura.js)
  const filteredCasas = useMemo(() => {
    return casas.filter((c) => {
      const matchRed =
        !selectedRedId ||
        selectedRedId === 'all' ||
        String(c.red_id) === String(selectedRedId);

      const matchSearch =
        search === '' ||
        (c.codigo && c.codigo.toLowerCase().includes(search.toLowerCase())) ||
        (c.nombre && c.nombre.toLowerCase().includes(search.toLowerCase())) ||
        (c.anfitrion && c.anfitrion.toLowerCase().includes(search.toLowerCase())) ||
        (c.lider && c.lider.toLowerCase().includes(search.toLowerCase())) ||
        (c.zona && c.zona.toLowerCase().includes(search.toLowerCase())) ||
        (c.direccion && c.direccion.toLowerCase().includes(search.toLowerCase()));

      let matchEstado = true;
      if (filtroEstado === 'pendientes_7d') {
        matchEstado = Boolean(c.sin_reporte_7d && c.is_active);
      } else if (filtroEstado === 'activas') {
        matchEstado = Boolean(c.is_active);
      }

      return matchRed && matchSearch && matchEstado;
    });
  }, [casas, selectedRedId, search, filtroEstado]);

  // Contadores para badges y banners
  const totalCasasCongregacion = casas.length;
  const totalPendientesCongregacion = useMemo(() => {
    return casas.filter((c) => c.sin_reporte_7d && c.is_active).length;
  }, [casas]);

  // Pendientes dentro del alcance de la vista actual (por red o congregación)
  const pendingInScope = useMemo(() => {
    if (selectedRedId && selectedRedId !== 'all') {
      return casas.filter((c) => Number(c.red_id) === Number(selectedRedId) && c.sin_reporte_7d && c.is_active).length;
    }
    return totalPendientesCongregacion;
  }, [casas, selectedRedId, totalPendientesCongregacion]);

  // Manejo de CRUD de Redes
  const handleGuardarRed = async (data: RedInput) => {
    try {
      if (redModalData.red) {
        const res = await editarRed({ id: redModalData.red.id, data });
        if (res.success) {
          success(res.message || 'Red ministerial actualizada correctamente.');
          refetchRedes();
        } else {
          error(res.message || 'Error al actualizar red.');
        }
      } else {
        const res = await crearRed(data);
        if (res.success) {
          success(res.message || 'Red ministerial creada exitosamente.');
          refetchRedes();
        } else {
          error(res.message || 'Error al crear red.');
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const handleToggleRed = async (id: number) => {
    try {
      const res = await toggleRed(id);
      if (res.success) {
        success(res.message || 'Estado de la red alternado.');
        refetchRedes();
      } else {
        error(res.message || 'Error al alternar estado.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const handleEliminarRed = async (id: number) => {
    try {
      const res = await eliminarRed(id);
      if (res.success) {
        success(res.message || 'Red ministerial eliminada.');
        refetchRedes();
        if (String(selectedRedId) === String(id)) {
          setFilter('red_id', '');
        }
      } else {
        error(res.message || 'No se pudo eliminar la red.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  // Manejo de CRUD de Casas de Paz
  const handleGuardarCdp = async (data: CdpInput) => {
    try {
      if (cdpModalData.casa) {
        const res = await editarCdp({ id: cdpModalData.casa.id, data });
        if (res.success) {
          success(res.message || 'Casa de Paz actualizada exitosamente.');
          refetchCasas();
        } else {
          error(res.message || 'Error al actualizar Casa de Paz.');
        }
      } else {
        const res = await crearCdp(data);
        if (res.success) {
          success(res.message || 'Casa de Paz creada exitosamente.');
          refetchCasas();
        } else {
          error(res.message || 'Error al crear Casa de Paz.');
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const handleEliminarCdp = async (id: number) => {
    try {
      const res = await eliminarCdp(id);
      if (res.success) {
        success(res.message || 'Casa de Paz eliminada.');
        refetchCasas();
      } else {
        error(res.message || 'No se pudo eliminar la Casa de Paz.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const dismissToast = () => {
    sessionStorage.setItem('reportes_toast_dismissed', '1');
    setShowToast(false);
  };

  // Paridad Jinja2/estructura.js: auto-cerrar toast tras 7 segundos
  useEffect(() => {
    if (showToast && totalPendientesCongregacion > 0) {
      const timer = setTimeout(() => {
        dismissToast();
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [showToast, totalPendientesCongregacion]);

  return (
    <main className={`estructura-main ${isSupervisor ? 'supervisor-mode' : ''}`}>
      {/* Header Canónico */}
      <header className="page-header">
        <div className="header-text">
          {isSupervisor ? (
            <>
              <h1 className="title">Estructura de mi Red</h1>
              <p className="subtitle">
                Supervisa el estado de tus <span className="highlight">Casas de Paz</span> y monitorea el crecimiento espiritual de cada grupo bajo tu responsabilidad.
              </p>
            </>
          ) : (
            <>
              <h1 className="title">Estructura Organizacional</h1>
              <p className="subtitle">
                Gestiona la arquitectura de tu comunidad a través de <span className="highlight">Redes</span> y <span className="highlight">Casas de Paz</span>. Define jerarquías y supervisa el crecimiento espiritual de cada grupo.
              </p>
            </>
          )}
        </div>

        {!isSupervisor && (
          <div className="header-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => setRedModalData({ isOpen: true, red: null })}
            >
              <Icon name="hub" size={18} className="mr-1.5 shrink-0" />
              Nueva Red
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setCdpModalData({ isOpen: true, casa: null })}
            >
              <Icon name="add_home" size={18} className="mr-1.5 shrink-0" />
              Nueva Casa de Paz
            </button>
          </div>
        )}
      </header>

      {/* Grid Principal: 2 columnas en Desktop, barra de chips en móvil */}
      <div className="estructura-grid">
        <div className="redes-sidebar-wrapper">
          {/* Flechas de navegación para chips: solo en dispositivos no táctiles (con ratón) */}
          {!isTouchDevice && (
            <>
              <button
                type="button"
                className={`scroll-arrow scroll-arrow-left ${canScrollLeft ? 'visible' : ''}`}
                onClick={() => handleScrollSidebar('left')}
                aria-label="Desplazar a la izquierda"
              >
                <ChevronLeft />
              </button>
              <button
                type="button"
                className={`scroll-arrow scroll-arrow-right ${canScrollRight ? 'visible' : ''}`}
                onClick={() => handleScrollSidebar('right')}
                aria-label="Desplazar a la derecha"
              >
                <ChevronRight />
              </button>
            </>
          )}

          <aside className="redes-sidebar" ref={sidebarRef}>
            <div className="sidebar-header">
              <h2 className="sidebar-title">{isSupervisor ? 'Mi Red' : 'Redes Activas'}</h2>
              <span className="badge badge-secondary">
                {redes.length} {redes.length === 1 ? 'Red' : 'Redes'}
              </span>
            </div>

            <div className="redes-list">
              {!isSupervisor && (
                <div
                  className={`red-card red-card-all ${
                    !selectedRedId || selectedRedId === 'all' ? 'active' : ''
                  }`}
                >
                  <button
                    type="button"
                    className="red-filter-trigger"
                    onClick={() => handleSelectRed('')}
                    aria-pressed={!selectedRedId || selectedRedId === 'all'}
                  >
                    <div className="red-header">
                      <span className="red-name">Todas las redes</span>
                      {totalPendientesCongregacion > 0 && (
                        <span className="red-pending-badge">
                          {totalPendientesCongregacion} pend.
                        </span>
                      )}
                    </div>
                    <p className="red-leader">Vista general</p>
                    <div className="red-stats">
                      <span className="red-count">
                        {totalCasasCongregacion}{' '}
                        {totalCasasCongregacion === 1 ? 'Casa Vinculada' : 'Casas Vinculadas'}
                      </span>
                    </div>
                  </button>
                </div>
              )}

              {redes.map((r) => {
                const isSelected = String(selectedRedId) === String(r.id);
                const isPaused = !r.is_active;
                const casasInRed = casas.filter((c) => Number(c.red_id) === Number(r.id)).length;
                const pendientesInRed = casas.filter(
                  (c) => Number(c.red_id) === Number(r.id) && c.sin_reporte_7d && c.is_active
                ).length;
                const displayName = cleanRedName(r.nombre);

                const isMenuOpen = activeMenuRedId === r.id;

                return (
                  <div
                    key={r.id}
                    className={`red-card ${isSelected ? 'active' : ''} ${
                      isPaused ? 'red-card-paused' : ''
                    } ${isMenuOpen ? 'menu-open' : ''}`}
                    style={{ zIndex: isMenuOpen ? 50 : undefined }}
                  >
                    <button
                      type="button"
                      className="red-filter-trigger"
                      onClick={() => handleSelectRed(r.id)}
                      aria-pressed={isSelected}
                    >
                      <div className="red-header">
                        <span className="red-name">Red {displayName}</span>
                        {isPaused && <span className="badge badge-warning">En pausa</span>}
                        {pendientesInRed > 0 && (
                          <span className="red-pending-badge">{pendientesInRed} pend.</span>
                        )}
                      </div>
                      <p className="red-leader">
                        Supervisor: {r.supervisor_nombre || r.supervisor || 'Sin asignar'}
                      </p>
                      <div className="red-stats">
                        {casasInRed > 0 && (
                          <div className="avatars">
                            <span className="avatar-circle avatar-maroon">
                              <Home />
                            </span>
                            {casasInRed > 1 && (
                              <span className="avatar-circle avatar-maroon">
                                <Home />
                              </span>
                            )}
                            {casasInRed > 2 && (
                              <span className="avatar-circle avatar-count">
                                +{casasInRed - 2}
                              </span>
                            )}
                          </div>
                        )}
                        <span className="red-count">
                          {casasInRed} {casasInRed === 1 ? 'Casa Vinculada' : 'Casas Vinculadas'}
                        </span>
                      </div>
                    </button>

                    {!isSupervisor && (
                      <button
                        type="button"
                        className="icon-more menu-trigger"
                        aria-label={`Opciones de ${r.nombre}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (activeMenuRedId === r.id) {
                            setActiveMenuRedId(null);
                            setActiveMenuRed(null);
                            setMenuPos(null);
                          } else {
                            const rect = e.currentTarget.getBoundingClientRect();
                            const menuHeight = 145;
                            const opensUpward = rect.bottom + menuHeight > window.innerHeight;
                            setMenuPos({
                              top: opensUpward ? Math.max(8, rect.top - menuHeight - 4) : rect.bottom + 4,
                              right: Math.max(8, window.innerWidth - rect.right),
                            });
                            setActiveMenuRedId(r.id);
                            setActiveMenuRed(r);
                          }
                        }}
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                );
              })}

              {redes.length === 0 && (
                <div className="empty-state empty-state-sidebar">
                  <Network />
                  <strong>Sin redes registradas</strong>
                  <span>Crea una red para comenzar.</span>
                </div>
              )}
            </div>

            {/* Tarjeta de Resumen de Impacto */}
            <div className="impact-card">
              <div className="impact-content">
                <h3>{isSupervisor ? 'Estado de Salud de mi Red' : 'Resumen de Impacto'}</h3>
                <p className="impact-subtitle">
                  {isSupervisor
                    ? 'Casas de Paz activas y reportando'
                    : 'Total alcance de redes'}
                </p>
                <div className="impact-number">{totalCasasCongregacion}</div>
                <p className="impact-note">Casas de Paz registradas</p>
              </div>
              <div className="watermark-icon">
                <Users />
              </div>
            </div>
          </aside>
        </div>

        {/* Sección Principal de Casas de Paz */}
        <section className="casas-section">
          <div className="casas-header">
            <div>
              <h3 className="section-title">Casas de Paz</h3>
              <p className="section-subtitle">
                Mostrando las casas de{' '}
                <strong id="casasFilterLabel">
                  {filtroEstado === 'pendientes_7d'
                    ? `${selectedRedName} (solo pendientes)`
                    : selectedRedName}
                </strong>
                {selectedRedObj && !isSupervisor && (
                  <button
                    type="button"
                    className="btn-mobile-manage-red"
                    onClick={() => setIsMobileSheetOpen(true)}
                    aria-label={`Gestionar ${selectedRedObj.nombre}`}
                    title="Gestionar red"
                  >
                    <MoreVertical className="w-3.5 h-3.5" />
                    <span>Opciones</span>
                  </button>
                )}
              </p>
            </div>
            <div className="search-bar">
              <span className="icon-search">
                <Search className="w-4 h-4" />
              </span>
              <input
                type="text"
                id="casasSearchInput"
                value={search}
                onChange={(e) => handleSearchChange(e.target.value)}
                placeholder="Buscar por código, líder, anfitrión o zona..."
                aria-label="Buscar Casas de Paz"
              />
            </div>
          </div>

          {/* Banner de Reportes de la Semana Pendientes */}
          {pendingInScope > 0 ? (
            <div
              className="alert-banner-reportes"
              id="bannerReportesPendientes"
              data-total-pendientes={pendingInScope}
            >
              <div className="alert-banner-main">
                <Icon
                  name="notification_important"
                  size={26}
                  className="alert-banner-icon shrink-0"
                />
                <div className="alert-banner-info">
                  <strong className="alert-banner-title">
                    {selectedRedId && selectedRedId !== 'all'
                      ? `Reportes Pendientes · ${selectedRedName}`
                      : 'Reportes de la Semana Pendientes'}
                  </strong>
                  <p className="alert-banner-text">
                    <strong>
                      {pendingInScope} Casa{pendingInScope !== 1 ? 's' : ''} de Paz activa
                      {pendingInScope !== 1 ? 's' : ''}
                    </strong>{' '}
                    {selectedRedId && selectedRedId !== 'all'
                      ? `en la ${selectedRedName}`
                      : 'en la congregación'}{' '}
                    no ha{pendingInScope !== 1 ? 'n' : ''} enviado reporte en los últimos 7 días.
                  </p>
                </div>
              </div>
              <div className="alert-banner-actions">
                {filtroEstado === 'pendientes_7d' ? (
                  <button
                    type="button"
                    className="btn-banner-filter btn-banner-all"
                    id="btnVerTodasCasas"
                    onClick={() => handleFiltroEstadoChange('todas')}
                    title="Mostrar todas las casas"
                  >
                    <Icon name="restart_alt" size={16} />
                    <span>Ver todas</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn-banner-filter"
                    id="btnFiltrarPendientes"
                    onClick={() => handleFiltroEstadoChange('pendientes_7d')}
                    title="Filtrar cuadrícula para ver solo casas pendientes"
                  >
                    <Icon name="filter_list" size={16} />
                    <span>
                      Ver {pendingInScope} pendiente{pendingInScope !== 1 ? 's' : ''}
                    </span>
                  </button>
                )}
              </div>
            </div>
          ) : selectedRedId && selectedRedId !== 'all' && filteredCasas.length > 0 ? (
            <div className="alert-banner-reportes is-all-good">
              <div className="alert-banner-main">
                <div className="alert-banner-icon">
                  <CheckCircle className="w-6 h-6" />
                </div>
                <div className="alert-banner-info">
                  <strong className="alert-banner-title">¡Red al día! · {selectedRedName}</strong>
                  <p className="alert-banner-text">
                    Todas las Casas de Paz activas de la <strong>{selectedRedName}</strong> han
                    enviado su reporte en los últimos 7 días.
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {/* Cuadrícula de Casas de Paz */}
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
              <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
                Cargando estructura de Casas de Paz...
              </p>
            </div>
          ) : (
            <div className="casas-grid">
              {filteredCasas.map((casa) => {
                const isHighlighted = highlightedCdpId === String(casa.id);
                const isPaused = !casa.is_active;
                const hasPending = Boolean(casa.sin_reporte_7d && casa.is_active);

                return (
                  <article
                    key={casa.id}
                    className={`casa-card ${isHighlighted ? 'casa-card-highlighted' : ''}`}
                    id={`cdp-${casa.id}`}
                  >
                    <div className="casa-header">
                      <div className="casa-info-top">
                        <div className="casa-icon">
                          <Home />
                        </div>
                        <div>
                          <h4 className="casa-name">Casa "{casa.codigo || casa.nombre}"</h4>
                          <span className="casa-zone">
                            {casa.zona || casa.direccion || 'Sin zona asignada'}
                          </span>
                        </div>
                      </div>
                      <div className="casa-status-wrap">
                        {isPaused ? (
                          <span className="status status-pausada" title="Casa en pausa / inactiva">
                            <span className="status-dot status-inactive-dot" aria-hidden="true" />{' '}
                            PAUSADA
                          </span>
                        ) : hasPending ? (
                          <span
                            className="status status-pendiente"
                            title="Sin reporte en los últimos 7 días"
                          >
                            <Clock className="w-3 h-3" /> SIN REPORTE
                          </span>
                        ) : (
                          <span className="status status-activa" title="Reportó en los últimos 7 días">
                            <span className="status-dot status-active-dot" aria-hidden="true" /> AL
                            DÍA
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="casa-details">
                      {casa.lider && (
                        <div className="detail-row">
                          <Shield className="w-4 h-4" />
                          <span>
                            Líder: <strong>{casa.lider}</strong>
                          </span>
                        </div>
                      )}
                      <div className="detail-row">
                        <User className="w-4 h-4" />
                        <span>
                          Anfitrión: <strong>{casa.anfitrion || 'Sin anfitrión'}</strong>
                        </span>
                      </div>
                      {casa.usuario_username ? (
                        <div className="detail-row">
                          <BadgeCheck className="w-4 h-4" />
                          <span>
                            Usuario: <strong>@{casa.usuario_username}</strong>
                            {casa.usuario_nombre && (
                              <small className="text-subtle"> ({casa.usuario_nombre})</small>
                            )}
                          </span>
                        </div>
                      ) : casa.usuario_nombre ? (
                        <div className="detail-row">
                          <BadgeCheck className="w-4 h-4" />
                          <span>
                            Usuario: <strong>{casa.usuario_nombre}</strong>
                          </span>
                        </div>
                      ) : null}
                      <div className="detail-row">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {casa.horario || `${casa.dia_semana || 'Miércoles'} · ${casa.hora || '7:00 PM'}`}
                        </span>
                      </div>
                    </div>

                    {/* Pie Canónico: Asistencia + Enlace Gestionar (Sin botones extras de llamada/whatsapp/pausa) */}
                    <div className="casa-footer">
                      <div className="attendance">
                        <Users className="w-4 h-4" />
                        <span>{casa.asistencia || 0} Asistentes promedio</span>
                      </div>
                      <Link to={`/casa-de-paz/${casa.id}`} className="btn-manage">
                        <span>Gestionar</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </article>
                );
              })}

              {/* Botón / Tarjeta Añadir Casa al final de la cuadrícula (para administradores, solo en una red específica) */}
              {isAdmin &&
                selectedRedId &&
                selectedRedId !== 'all' &&
                filtroEstado !== 'pendientes_7d' &&
                !search && (
                  <button
                    type="button"
                    className="casa-add-card"
                    onClick={() => setCdpModalData({ isOpen: true, casa: null })}
                  >
                    <div className="add-icon">
                      <Plus />
                    </div>
                    <h4>Registrar Nueva Casa</h4>
                    <p>Asigna un nuevo anfitrión y vincula la ubicación a esta red.</p>
                  </button>
                )}

              {/* Estados Vacíos */}
              {filteredCasas.length === 0 && (
                <div className="empty-state empty-state-casas">
                  {filtroEstado === 'pendientes_7d' ? (
                    <>
                      <CheckCircle className="w-10 h-10 text-emerald-600 mb-2" />
                      <strong className="text-emerald-700">¡Al día con los reportes!</strong>
                      <span>
                        No hay Casas de Paz activas pendientes de reporte en esta vista.
                      </span>
                      <button
                        type="button"
                        className="btn-banner-filter btn-banner-all mt-3 cursor-pointer"
                        onClick={() => handleFiltroEstadoChange('todas')}
                      >
                        <Icon name="restart_alt" size={16} className="mr-1" />
                        <span>Ver todas las casas</span>
                      </button>
                    </>
                  ) : (
                    <>
                      <Home className="w-10 h-10 text-neutral-400 mb-2" />
                      <strong>Sin Casas de Paz registradas</strong>
                      <span>Esta red todavía no tiene casas vinculadas.</span>
                    </>
                  )}
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      {/* Toast Flotante de Cumplimiento Semanal */}
      {showToast && totalPendientesCongregacion > 0 && (
        <div className="toast-estructura is-visible" role="alert">
          <div className="toast-content">
            <div className="toast-icon">
              <Icon name="notification_important" size={20} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div className="toast-texts">
              <strong>Cumplimiento Semanal</strong>
              <span>
                {totalPendientesCongregacion} Casa
                {totalPendientesCongregacion > 1 ? 's' : ''} de Paz activa
                {totalPendientesCongregacion > 1 ? 's' : ''} sin reporte en los últimos 7 días.
              </span>
            </div>
          </div>
          <div className="toast-actions">
            <button
              type="button"
              className="toast-btn-action"
              onClick={() => {
                dismissToast();
                handleFiltroEstadoChange('pendientes_7d');
                const sec = document.querySelector('.casas-section');
                if (sec) sec.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Ver
            </button>
            <button
              type="button"
              className="toast-btn-close"
              aria-label="Cerrar notificación"
              onClick={dismissToast}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Modal CRUD de Red */}
      {redModalData.isOpen && (
        <RedModal
          isOpen={redModalData.isOpen}
          onClose={() => setRedModalData({ isOpen: false, red: null })}
          red={redModalData.red}
          supervisores={selectores?.supervisores || []}
          onSave={handleGuardarRed}
          onDelete={handleEliminarRed}
          isSaving={isCreandoRed || isEditandoRed}
          isDeleting={isEliminandoRed}
        />
      )}

      {/* Modal CRUD de Casa de Paz */}
      {cdpModalData.isOpen && (
        <CasaDePazModal
          isOpen={cdpModalData.isOpen}
          onClose={() => setCdpModalData({ isOpen: false, casa: null })}
          casa={cdpModalData.casa}
          redes={redes}
          lideresDisponibles={selectores?.lideres_cdp || []}
          defaultRedId={selectedRedId && selectedRedId !== 'all' ? selectedRedId : undefined}
          onSave={handleGuardarCdp}
          onDelete={handleEliminarCdp}
          isSaving={isCreandoCdp || isEditandoCdp}
          isDeleting={isEliminandoCdp}
        />
      )}

      {/* Portal del Menú Contextual de Red para Desktop (Evita recortes de overflow y stacking context) */}
      {activeMenuRed && menuPos && createPortal(
        <div
          className="red-menu is-open"
          role="menu"
          style={{
            position: 'fixed',
            top: `${menuPos.top}px`,
            right: `${menuPos.right}px`,
            zIndex: 99999,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              const target = activeMenuRed;
              setActiveMenuRedId(null);
              setActiveMenuRed(null);
              setMenuPos(null);
              setRedModalData({ isOpen: true, red: target });
            }}
          >
            <Edit className="w-3.5 h-3.5" />
            <span>Editar red</span>
          </button>
          <button
            type="button"
            role="menuitem"
            className={activeMenuRed.is_active ? 'menu-danger' : 'menu-success'}
            onClick={() => {
              const targetId = activeMenuRed.id;
              setActiveMenuRedId(null);
              setActiveMenuRed(null);
              setMenuPos(null);
              handleToggleRed(targetId);
            }}
          >
            {activeMenuRed.is_active ? (
              <>
                <PauseCircle className="w-3.5 h-3.5" />
                <span>Poner en pausa</span>
              </>
            ) : (
              <>
                <PlayCircle className="w-3.5 h-3.5" />
                <span>Reactivar red</span>
              </>
            )}
          </button>
          {isAdmin && (
            <button
              type="button"
              role="menuitem"
              className="menu-danger"
              onClick={() => {
                const targetId = activeMenuRed.id;
                setActiveMenuRedId(null);
                setActiveMenuRed(null);
                setMenuPos(null);
                handleEliminarRed(targetId);
              }}
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Eliminar red</span>
            </button>
          )}
        </div>,
        document.body
      )}

      {/* Bottom Sheet de Opciones de Red para Móvil (Opción 1) */}
      <RedBottomSheet
        isOpen={isMobileSheetOpen}
        onClose={() => setIsMobileSheetOpen(false)}
        red={selectedRedObj || null}
        isAdmin={isAdmin}
        onEdit={(red) => setRedModalData({ isOpen: true, red })}
        onToggle={handleToggleRed}
        onDelete={handleEliminarRed}
      />
    </main>
  );
};
