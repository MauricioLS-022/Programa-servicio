import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { DashboardKpiCards } from '../DashboardKpiCards';
import type { DashboardMetricas } from '../../../types/estructura';

describe('DashboardKpiCards Component', () => {
  it('renderiza "Sin datos" en Vista General cuando total_casas es 0 o ausente', () => {
    const emptyMetricas: DashboardMetricas = {
      total_asistencia: 0,
      total_casas: 0,
      cumplimiento: 0,
      ofrendas_usd: 0,
      ofrendas_bs: 0,
      conversiones: 0,
    };

    render(
      <DashboardKpiCards
        metricas={emptyMetricas}
        nivel="general"
        periodo="semana"
      />
    );

    const sinDatosList = screen.getAllByText('Sin datos');
    expect(sinDatosList.length).toBeGreaterThanOrEqual(4);
  });

  it('despliega los valores correctos y formateados cuando hay datos en Vista General', () => {
    const mockMetricas: DashboardMetricas = {
      total_asistencia: 154,
      total_casas: 12,
      casas_con_reporte: 10,
      cumplimiento: 83,
      ofrendas_usd: 450.75,
      ofrendas_bs: 15800.5,
      conversiones: 18,
    };

    render(
      <DashboardKpiCards
        metricas={mockMetricas}
        nivel="general"
        periodo="semana"
      />
    );

    expect(screen.getByText('154')).toBeInTheDocument();
    expect(screen.getByText('83%')).toBeInTheDocument();
    expect(screen.getByText('10 de 12 CDP')).toBeInTheDocument();
    expect(screen.getByText('$450.75')).toBeInTheDocument();
    expect(screen.getByText('Bs. 15.800,50')).toBeInTheDocument();
    expect(screen.getByText('18')).toBeInTheDocument();
  });

  it('renderiza "Sin datos" en Nivel Red cuando no hay casas activas', () => {
    const emptyRedMetricas: DashboardMetricas = {
      nombre_red: 'Red Vacía',
      asistencia_total: 0,
      casas_activas: 0,
      casas: [],
    };

    render(
      <DashboardKpiCards
        metricas={emptyRedMetricas}
        nivel="red"
        periodo="semana"
      />
    );

    const sinDatosList = screen.getAllByText('Sin datos');
    expect(sinDatosList.length).toBeGreaterThanOrEqual(4);
  });

  it('renderiza métricas zonales correctas en Nivel Red con casas activas', () => {
    const redMetricas: DashboardMetricas = {
      nombre_red: 'Red Hebrón',
      asistencia_total: 65,
      casas_activas: 4,
      promedio_casa: 16,
      conversiones: 8,
      ofrendas_usd: 120.0,
      ofrendas_bs: 4200.0,
      casas: [{ id: 1, codigo: 'HEB-001', red_id: 1, lider: 'Líder 1', asistencia: 20, visitas: 3 }],
    };

    render(
      <DashboardKpiCards
        metricas={redMetricas}
        nivel="red"
        periodo="semana"
      />
    );

    expect(screen.getByText('65')).toBeInTheDocument();
    expect(screen.getByText('16')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('$120.00')).toBeInTheDocument();
  });

  it('renderiza los 4 KPIs específicos de Casa de Paz y oculta Bs cuando es 0', () => {
    const cdpMetricas: DashboardMetricas = {
      asistencia_ultimo: 24,
      promedio_historico: 21,
      ofrendas_usd: 50.0,
      ofrendas_bs: 0.0,
      estado_reporte: 'enviado',
      historial: [
        { fecha: '2026-10-18', asistencia: 24, ninos: 4, visitas: 5, ofrendas_usd: 50.0, ofrendas_bs: 0.0 }
      ],
    };

    render(
      <DashboardKpiCards
        metricas={cdpMetricas}
        nivel="cdp"
        periodo="semana"
      />
    );

    expect(screen.getByText('24')).toBeInTheDocument();
    expect(screen.getByText('21')).toBeInTheDocument();
    expect(screen.getByText('$50.00')).toBeInTheDocument();
    expect(screen.queryByText(/Bs\./)).not.toBeInTheDocument();
    expect(screen.getByText('Al día (Esta semana)')).toBeInTheDocument();
  });
});

