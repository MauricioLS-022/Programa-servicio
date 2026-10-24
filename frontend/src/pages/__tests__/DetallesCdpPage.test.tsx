import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { DetallesCdpPage } from '../DetallesCdpPage';
import type { CdpDetalle } from '../../types/estructura';

// Mocks
const mockSuccess = vi.fn();
const mockError = vi.fn();
vi.mock('../../context/ToastContext', () => ({
  useToast: () => ({
    success: mockSuccess,
    error: mockError,
    warning: vi.fn(),
    info: vi.fn(),
  }),
}));

let mockUser: any = {
  id: '1',
  username: 'admin',
  rol: 'admin',
  nombre: 'Administrador',
};

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
  }),
}));

const mockCdpDetalleData: CdpDetalle = {
  id: 10,
  codigo: 'HEB-001',
  nombre: 'Casa Hebrón Uno',
  red_id: 1,
  red_nombre: 'Red Hebrón',
  supervisor_id: 2,
  supervisor_nombre: 'Pedro Pérez',
  direccion: 'Calle 12 #18-45, sector El Carmen',
  maps_url: 'https://maps.google.com/?q=test',
  anfitrion: 'Familia Mendoza',
  usuario_id: 5,
  usuario_username: 'carlosm',
  usuario_nombre: 'Carlos',
  usuario_apellido: 'Mendoza',
  lider_id: 5,
  lider_nombre: 'Carlos Mendoza',
  telefono: '+584121234567',
  telefono_wa: '584121234567',
  horario: 'Miércoles · 7:00 PM',
  is_active: 1,
  asistencia_promedio: 22,
  total_reportes: 15,
  ofrendas_usd_totales: 120.5,
  ofrendas_bs_totales: 4500.0,
  visitas_totales: 30,
  conversiones_totales: 12,
  reporte_reciente_7d: true,
  estado_reporte_7d: 'al_dia',
  dias_desde_ultimo_reporte: 2,
  lideres: [
    {
      id: 5,
      nombre_completo: 'Carlos Mendoza',
      rol: 'Líder Principal',
      telefono: '+584121234567',
      telefono_wa: '584121234567',
      iniciales: 'CM',
    },
  ],
  reportes: [
    {
      id: 101,
      fecha: '2026-10-20',
      fecha_formateada: '20/10/2026',
      tema: 'El poder de la oración',
      observaciones: 'Reunión muy bendecida con visitantes.',
      asistencia: 24,
      nro_regulares: 14,
      nro_ninos: 6,
      nro_visitas: 4,
      ofrendas_usd: 15.0,
      ofrendas_bs: 600.0,
      cesta_amor: 1,
    },
  ],
};

const mockRefetch = vi.fn();
const mockToggleCdp = vi.fn().mockResolvedValue({ success: true, message: 'Estado modificado' });
const mockEditarCdp = vi.fn().mockResolvedValue({ success: true, message: 'Casa editada' });
const mockCrearLider = vi.fn().mockResolvedValue({ success: true, message: 'Líder asignado' });
const mockEditarLider = vi.fn().mockResolvedValue({ success: true, message: 'Líder actualizado' });

vi.mock('../../hooks/useEstructura', () => ({
  useCdpDetalle: () => ({
    cdp: mockCdpDetalleData,
    isLoading: false,
    isError: false,
    refetch: mockRefetch,
  }),
  useEstructuraSelectores: () => ({
    selectores: {
      redes: [{ id: 1, nombre: 'Red Hebrón' }],
      lideres_cdp: [],
      supervisores: [],
      casas_de_paz: [],
    },
  }),
  useEstructuraMutations: () => ({
    toggleCdp: mockToggleCdp,
    isTogglingCdp: false,
    editarCdp: mockEditarCdp,
    isEditandoCdp: false,
    crearLider: mockCrearLider,
    isCreandoLider: false,
    editarLider: mockEditarLider,
    isEditandoLider: false,
  }),
}));

describe('DetallesCdpPage Component (Paridad Jinja2 detalles_cdp.html)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renderiza la Ficha Técnica canónica con encabezado, los 6 KPIs balanceados, equipo e historial', () => {
    render(
      <MemoryRouter initialEntries={['/casa-de-paz/10']}>
        <Routes>
          <Route path="/casa-de-paz/:id" element={<DetallesCdpPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Encabezado
    expect(screen.getByText('Ficha Informativa · Casa de Paz')).toBeInTheDocument();
    expect(screen.getByText('Casa "HEB-001"')).toBeInTheDocument();
    expect(screen.getByText('Red Hebrón')).toBeInTheDocument();
    expect(screen.getByText('Pedro Pérez')).toBeInTheDocument();

    // 6 KPIs Bento Grid
    expect(screen.getByText('Asistencia Prom.')).toBeInTheDocument();
    expect(screen.getByText('22')).toBeInTheDocument();
    expect(screen.getByText('Reportes')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('Ofrendas Totales')).toBeInTheDocument();
    expect(screen.getByText('$120.50')).toBeInTheDocument();
    expect(screen.getByText('Visitas')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText('Fruto Espiritual')).toBeInTheDocument();
    expect(screen.getByText('Pulso Semanal')).toBeInTheDocument();
    expect(screen.getByText('Al día')).toBeInTheDocument();

    // Información del Centro
    expect(screen.getByText('Calle 12 #18-45, sector El Carmen')).toBeInTheDocument();
    expect(screen.getByText('Familia Mendoza')).toBeInTheDocument();
    expect(screen.getByText('@carlosm')).toBeInTheDocument();

    // Equipo ministerial
    expect(screen.getByText('Responsables Asignados')).toBeInTheDocument();
    expect(screen.getByText('Carlos Mendoza')).toBeInTheDocument();
    expect(screen.getByText('Líder Principal')).toBeInTheDocument();

    // Historial reciente de reportes
    expect(screen.getByText('Últimos Reportes Semanales')).toBeInTheDocument();
    expect(screen.getByText('El poder de la oración')).toBeInTheDocument();
    expect(screen.getByText('24 pers.')).toBeInTheDocument();
  });

  it('permite abrir el modal para Añadir Líder a la Casa de Paz', () => {
    render(
      <MemoryRouter initialEntries={['/casa-de-paz/10']}>
        <Routes>
          <Route path="/casa-de-paz/:id" element={<DetallesCdpPage />} />
        </Routes>
      </MemoryRouter>
    );

    const btnAnadirLider = screen.getByRole('button', { name: /Añadir líder a la Casa de Paz/i });
    expect(btnAnadirLider).toBeInTheDocument();
    fireEvent.click(btnAnadirLider);

    expect(screen.getByText('Añadir Líder a Casa de Paz')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ej: Carlos')).toBeInTheDocument();
  });

  it('permite alternar el estado de la Casa de Paz al hacer clic en Pausar Casa', async () => {
    render(
      <MemoryRouter initialEntries={['/casa-de-paz/10']}>
        <Routes>
          <Route path="/casa-de-paz/:id" element={<DetallesCdpPage />} />
        </Routes>
      </MemoryRouter>
    );

    const btnPausar = screen.getByRole('button', { name: /Pausar Casa/i });
    fireEvent.click(btnPausar);

    await waitFor(() => {
      expect(mockToggleCdp).toHaveBeenCalledWith(10);
      expect(mockSuccess).toHaveBeenCalledWith('Estado modificado');
    });
  });

  it('el botón Volver tiene enlace directo a /estructura', () => {
    render(
      <MemoryRouter initialEntries={['/casa-de-paz/10']}>
        <Routes>
          <Route path="/casa-de-paz/:id" element={<DetallesCdpPage />} />
        </Routes>
      </MemoryRouter>
    );

    const linkVolver = screen.getByRole('link', { name: /Volver/i });
    expect(linkVolver).toHaveAttribute('href', '/estructura');
  });

  it('el botón Exportar PDF está presente y es clickable', () => {
    render(
      <MemoryRouter initialEntries={['/casa-de-paz/10']}>
        <Routes>
          <Route path="/casa-de-paz/:id" element={<DetallesCdpPage />} />
        </Routes>
      </MemoryRouter>
    );

    const btnExportPdf = screen.getByRole('button', { name: /Exportar Ficha Técnica de Casa de Paz en PDF/i });
    expect(btnExportPdf).toBeInTheDocument();
    expect(() => fireEvent.click(btnExportPdf)).not.toThrow();
  });
});

