import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { ErrorBoundary } from '../ErrorBoundary';

// Componente defectuoso de prueba
const BrokenComponent: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error('Fallo crítico simulado en renderizado');
  }
  return <div>Componente funcional normal</div>;
};

describe('ErrorBoundary Component', () => {
  beforeEach(() => {
    // Silenciar error en console para mantener la salida del test limpia
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renderiza a los hijos sin alterar el DOM cuando no hay errores', () => {
    render(
      <ErrorBoundary>
        <div>Contenido ministerial seguro</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Contenido ministerial seguro')).toBeInTheDocument();
  });

  it('captura un error de renderizado y muestra la pantalla institucional de fallback 500', () => {
    render(
      <ErrorBoundary>
        <BrokenComponent shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('Error en el servidor')).toBeInTheDocument();
    expect(screen.getByText('Fallo crítico simulado en renderizado')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reintentar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Recargar página/i })).toBeInTheDocument();
    expect(screen.getByText('Vino Nuevo — Servicio Comunitario')).toBeInTheDocument();
  });

  it('permite reintentar el renderizado al pulsar Reintentar', () => {
    let throwError = true;
    const DynamicComponent = () => {
      if (throwError) {
        throw new Error('Error dinámico');
      }
      return <div>Recuperado con éxito</div>;
    };

    render(
      <ErrorBoundary>
        <DynamicComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error dinámico')).toBeInTheDocument();

    // Reparar la condición de fallo y hacer click en Reintentar
    throwError = false;
    fireEvent.click(screen.getByRole('button', { name: /Reintentar/i }));

    expect(screen.getByText('Recuperado con éxito')).toBeInTheDocument();
  });

  it('detecta errores de carga diferida de chunks (ChunkLoadError) y muestra acción para actualizar aplicación', () => {
    const BrokenChunkComponent = () => {
      const err = new Error('Failed to fetch dynamically imported module: /assets/DashboardPage.js');
      err.name = 'ChunkLoadError';
      throw err;
    };

    render(
      <ErrorBoundary>
        <BrokenChunkComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('SYNC')).toBeInTheDocument();
    expect(screen.getByText('Actualización o desconexión detectada')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Actualizar Aplicación/i })).toBeInTheDocument();
  });
});
