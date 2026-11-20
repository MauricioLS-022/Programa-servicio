import { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { useRedes, useCasasDePaz } from './useDashboard';
import { useEstructuraMutations, useEstructuraSelectores } from './useEstructura';
import { useAuth } from './useAuth';
import { useUrlFilters } from './useUrlFilters';
import { useToast } from '../context/ToastContext';
import type { Red, CasaDePaz, RedInput, CdpInput } from '../types/estructura';

export type FiltroEstadoEstructura = 'todas' | 'pendientes_7d' | 'activas';

/** Limpia prefijos duplicados ("Red Red Hebrón" -> "Hebrón"). */
export const cleanRedName = (name?: string) => (name ? name.replace(/^Red\s+/i, '').trim() : '');

/**
 * Hook controlador para la vista de Estructura Organizacional.
 * Centraliza filtros URL (SSOT), aislamiento territorial de supervisores,
 * filtrado client-side, deep linking, scroll de chips y mutaciones CRUD.
 */
export function useEstructuraController() {
  const { user } = useAuth();
  const { success, error } = useToast();
  const isAdmin = user?.rol === 'admin';
  const isSupervisor = user?.rol === 'supervisor';

  const defaultEstructuraFilters = useMemo(
    () => ({
      red_id: '',
      filtro: 'todas' as FiltroEstadoEstructura,
      q: '',
    }),
    []
  );

  const { filters, setFilter, setFilters, searchParams } = useUrlFilters(
    defaultEstructuraFilters,
    { cleanupKeys: ['cdp_id', 'casa_id'] }
  );

  const selectedRedId = filters.red_id;
  const filtroEstado = filters.filtro;
  const search = filters.q;
  const initialCdpId = useMemo(
    () => searchParams.get('cdp_id') || searchParams.get('casa_id') || '',
    // Solo evaluar en montaje inicial para deep linking
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );
  const [highlightedCdpId, setHighlightedCdpId] = useState<string | null>(initialCdpId || null);

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

  const [showToast, setShowToast] = useState(() => {
    return !sessionStorage.getItem('reportes_toast_dismissed');
  });

  const sidebarRef = useRef<HTMLElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    const hasTouch =
      typeof window !== 'undefined' &&
      ('ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        window.matchMedia('(pointer: coarse)').matches);
    setIsTouchDevice(Boolean(hasTouch));
  }, []);

  const checkScrollArrows = useCallback(() => {
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
  }, [isTouchDevice]);

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
  }, [redes, isTouchDevice, checkScrollArrows]);

  const handleScrollSidebar = useCallback((direction: 'left' | 'right') => {
    if (!sidebarRef.current) return;
    const SCROLL_AMOUNT = 150;
    sidebarRef.current.scrollBy({
      left: direction === 'left' ? -SCROLL_AMOUNT : SCROLL_AMOUNT,
      behavior: 'smooth',
    });
  }, []);

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

  const closeContextMenu = useCallback(() => {
    setActiveMenuRedId(null);
    setActiveMenuRed(null);
    setMenuPos(null);
  }, []);

  useEffect(() => {
    if (activeMenuRedId !== null) {
      document.addEventListener('click', closeContextMenu);
      window.addEventListener('resize', closeContextMenu);
      window.addEventListener('scroll', closeContextMenu, true);
      return () => {
        document.removeEventListener('click', closeContextMenu);
        window.removeEventListener('resize', closeContextMenu);
        window.removeEventListener('scroll', closeContextMenu, true);
      };
    }
  }, [activeMenuRedId, closeContextMenu]);

  const handleToggleContextMenu = useCallback(
    (red: Red, triggerEl: HTMLElement) => {
      if (activeMenuRedId === red.id) {
        closeContextMenu();
        return;
      }
      const rect = triggerEl.getBoundingClientRect();
      const menuHeight = 145;
      const opensUpward = rect.bottom + menuHeight > window.innerHeight;
      setMenuPos({
        top: opensUpward ? Math.max(8, rect.top - menuHeight - 4) : rect.bottom + 4,
        right: Math.max(8, window.innerWidth - rect.right),
      });
      setActiveMenuRedId(red.id);
      setActiveMenuRed(red);
    },
    [activeMenuRedId, closeContextMenu]
  );

  const handleSelectRed = useCallback(
    (id: number | string) => {
      const redStr = String(id === 'all' || !id ? '' : id);
      setFilters({ red_id: redStr }, ['cdp_id', 'casa_id']);
    },
    [setFilters]
  );

  const handleFiltroEstadoChange = useCallback(
    (estado: FiltroEstadoEstructura) => {
      setFilters({ filtro: estado }, ['cdp_id', 'casa_id']);
    },
    [setFilters]
  );

  const handleSearchChange = useCallback(
    (value: string) => {
      setFilters({ q: value }, ['cdp_id', 'casa_id']);
    },
    [setFilters]
  );

  const effectiveRedId = useMemo(() => {
    if (selectedRedId) return selectedRedId;
    if (isSupervisor && redes.length > 0) return String(redes[0].id);
    return '';
  }, [selectedRedId, isSupervisor, redes]);

  const selectedRedObj = useMemo(() => {
    if (!effectiveRedId || effectiveRedId === 'all') return null;
    return redes.find((r) => String(r.id) === String(effectiveRedId)) || null;
  }, [redes, effectiveRedId]);

  const selectedRedName = useMemo(() => {
    if (selectedRedObj) return `Red ${cleanRedName(selectedRedObj.nombre)}`;
    if (isSupervisor && redes.length > 0) return `Red ${cleanRedName(redes[0].nombre)}`;
    return 'todas las redes';
  }, [selectedRedObj, isSupervisor, redes]);

  const filteredCasas = useMemo(() => {
    return casas.filter((c) => {
      const matchRed =
        !effectiveRedId ||
        effectiveRedId === 'all' ||
        String(c.red_id) === String(effectiveRedId);

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
  }, [casas, effectiveRedId, search, filtroEstado]);

  const totalCasasCongregacion = casas.length;
  const totalPendientesCongregacion = useMemo(() => {
    return casas.filter((c) => c.sin_reporte_7d && c.is_active).length;
  }, [casas]);

  const pendingInScope = useMemo(() => {
    if (effectiveRedId && effectiveRedId !== 'all') {
      return casas.filter(
        (c) => Number(c.red_id) === Number(effectiveRedId) && c.sin_reporte_7d && c.is_active
      ).length;
    }
    return totalPendientesCongregacion;
  }, [casas, effectiveRedId, totalPendientesCongregacion]);

  const handleGuardarRed = useCallback(
    async (data: RedInput) => {
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
    },
    [redModalData.red, editarRed, crearRed, success, error, refetchRedes]
  );

  const handleToggleRed = useCallback(
    async (id: number) => {
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
    },
    [toggleRed, success, error, refetchRedes]
  );

  const handleEliminarRed = useCallback(
    async (id: number) => {
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
    },
    [eliminarRed, success, error, refetchRedes, selectedRedId, setFilter]
  );

  const handleGuardarCdp = useCallback(
    async (data: CdpInput) => {
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
    },
    [cdpModalData.casa, editarCdp, crearCdp, success, error, refetchCasas]
  );

  const handleEliminarCdp = useCallback(
    async (id: number) => {
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
    },
    [eliminarCdp, success, error, refetchCasas]
  );

  const dismissToast = useCallback(() => {
    sessionStorage.setItem('reportes_toast_dismissed', '1');
    setShowToast(false);
  }, []);

  useEffect(() => {
    if (showToast && totalPendientesCongregacion > 0) {
      const timer = setTimeout(() => {
        dismissToast();
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [showToast, totalPendientesCongregacion, dismissToast]);

  const activeRedModalData = useMemo(
    () => ({
      isOpen: redModalData.isOpen,
      red: redModalData.red
        ? redes.find((r) => String(r.id) === String(redModalData.red?.id)) ?? redModalData.red
        : null,
    }),
    [redModalData, redes]
  );

  const activeCdpModalData = useMemo(
    () => ({
      isOpen: cdpModalData.isOpen,
      casa: cdpModalData.casa
        ? casas.find((c) => String(c.id) === String(cdpModalData.casa?.id)) ?? cdpModalData.casa
        : null,
    }),
    [cdpModalData, casas]
  );

  return {
    isAdmin,
    isSupervisor,
    redes,
    casas,
    filteredCasas,
    isLoading,
    selectores,
    selectedRedId,
    effectiveRedId,
    selectedRedObj,
    selectedRedName,
    filtroEstado,
    search,
    highlightedCdpId,
    totalCasasCongregacion,
    totalPendientesCongregacion,
    pendingInScope,
    redModalData: activeRedModalData,
    setRedModalData,
    cdpModalData: activeCdpModalData,
    setCdpModalData,
    isCreandoRed,
    isEditandoRed,
    isEliminandoRed,
    isCreandoCdp,
    isEditandoCdp,
    isEliminandoCdp,
    activeMenuRedId,
    activeMenuRed,
    menuPos,
    closeContextMenu,
    handleToggleContextMenu,
    isMobileSheetOpen,
    setIsMobileSheetOpen,
    showToast,
    dismissToast,
    sidebarRef,
    isTouchDevice,
    canScrollLeft,
    canScrollRight,
    handleScrollSidebar,
    handleSelectRed,
    handleFiltroEstadoChange,
    handleSearchChange,
    handleGuardarRed,
    handleToggleRed,
    handleEliminarRed,
    handleGuardarCdp,
    handleEliminarCdp,
  };
}
