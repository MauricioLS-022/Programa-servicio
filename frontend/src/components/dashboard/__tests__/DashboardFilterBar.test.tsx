import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { DashboardFilterBar } from '../DashboardFilterBar';
import type { Red, CasaDePaz } from '../../../types/estructura';

describe('DashboardFilterBar Component', () => {
  const redesMock: Red[] = [
    { id: 1, nombre: 'Red Hebrón', is_active: 1 },
    { id: 2, nombre: 'Red Sur', is_active: 1 },
  ];

  const casasMock: CasaDePaz[] = [
    { id: 101, codigo: 'HEB-001', red_id: 1, anfitrion: 'Familia Gómez', is_active: 1 },
    { id: 102, codigo: 'HEB-002', red_id: 1, anfitrion: 'Familia Díaz', is_active: 1 },
    { id: 201, codigo: 'SUR-001', red_id: 2, anfitrion: 'Familia López', is_active: 1 },
  ];

  it('muestra selector de nivel completo para admin y restringe para supervisor', () => {
    const handleNivelChange = vi.fn();

    const { rerender } = render(
      <DashboardFilterBar
        rol="admin"
        nivel="general"
        onNivelChange={handleNivelChange}
        redId=""
        onRedChange={vi.fn()}
        redes={redesMock}
        cdpId=""
        onCdpChange={vi.fn()}
        casas={casasMock}
        searchQuery=""
        onSearchChange={vi.fn()}
        onReset={vi.fn()}
      />
    );

    expect(screen.getByRole('option', { name: 'Vista General (Iglesia)' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Por Red / Zonal' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Por Casa de Paz' })).toBeInTheDocument();

    rerender(
      <DashboardFilterBar
        rol="supervisor"
        nivel="red"
        onNivelChange={handleNivelChange}
        redId={1}
        onRedChange={vi.fn()}
        redes={redesMock}
        cdpId=""
        onCdpChange={vi.fn()}
        casas={casasMock}
        searchQuery=""
        onSearchChange={vi.fn()}
        onReset={vi.fn()}
      />
    );

    expect(screen.queryByRole('option', { name: 'Vista General (Iglesia)' })).not.toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Mi Red (Zonal)' })).toBeInTheDocument();
  });

  it('filtra Casas de Paz pertenecientes exclusivamente a la red seleccionada', () => {
    render(
      <DashboardFilterBar
        rol="admin"
        nivel="cdp"
        onNivelChange={vi.fn()}
        redId={1}
        onRedChange={vi.fn()}
        redes={redesMock}
        cdpId=""
        onCdpChange={vi.fn()}
        casas={casasMock}
        searchQuery=""
        onSearchChange={vi.fn()}
        onReset={vi.fn()}
      />
    );

    expect(screen.getByRole('option', { name: /HEB-001/ })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /HEB-002/ })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: /SUR-001/ })).not.toBeInTheDocument();
  });

  it('dispara onSearchChange al escribir en la búsqueda y permite limpiarla', () => {
    const handleSearchChange = vi.fn();

    render(
      <DashboardFilterBar
        rol="admin"
        nivel="general"
        onNivelChange={vi.fn()}
        redId=""
        onRedChange={vi.fn()}
        redes={redesMock}
        cdpId=""
        onCdpChange={vi.fn()}
        casas={casasMock}
        searchQuery="Bethel"
        onSearchChange={handleSearchChange}
        onReset={vi.fn()}
      />
    );

    const clearBtn = screen.getByTitle('Limpiar búsqueda');
    expect(clearBtn).toBeInTheDocument();
    fireEvent.click(clearBtn);
    expect(handleSearchChange).toHaveBeenCalledWith('');
  });
});

