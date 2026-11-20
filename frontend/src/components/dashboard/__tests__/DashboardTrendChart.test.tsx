import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { DashboardTrendChart } from '../DashboardTrendChart';

describe('DashboardTrendChart', () => {
  const redesSemana = [
    { semana: 'Cielos Abiertos', asistencia: 0, porcentaje: 0 },
    { semana: 'Red Sur', asistencia: 14, porcentaje: 100 },
    { semana: 'Enmanuel', asistencia: 0, porcentaje: 0 },
    { semana: 'Elohim', asistencia: 0, porcentaje: 0 },
    { semana: 'Hebron', asistencia: 0, porcentaje: 0 },
  ];

  it('no muestra el badge de variación en desglose categórico semanal (general)', () => {
    render(
      <DashboardTrendChart
        tendencia={redesSemana}
        promedioTendencia={3}
        periodo="semana"
        nivel="general"
      />
    );

    expect(screen.getByText('Asistencia por Red esta Semana')).toBeInTheDocument();
    expect(screen.getByText('Desglose por Red de los reportes de esta semana')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByText(/vs promedio/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/vs anterior/i)).not.toBeInTheDocument();
  });

  it('no muestra el badge de variación en desglose categórico semanal (red)', () => {
    render(
      <DashboardTrendChart
        tendencia={[
          { semana: 'SUR-001', asistencia: 14, porcentaje: 100 },
          { semana: 'SUR-002', asistencia: 0, porcentaje: 0 },
        ]}
        promedioTendencia={7}
        periodo="semana"
        nivel="red"
        redNombre="Red Sur"
      />
    );

    expect(screen.getByText('Asistencia por Casa esta Semana')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('muestra el badge de variación en series cronológicas (mes y año)', () => {
    render(
      <DashboardTrendChart
        tendencia={[
          { semana: 'Sem 1', asistencia: 20, porcentaje: 80 },
          { semana: 'Sem 2', asistencia: 25, porcentaje: 100 },
        ]}
        promedioTendencia={23}
        periodo="mes"
        periodoNombre="Noviembre 2026"
        nivel="general"
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('+25% vs anterior')).toBeInTheDocument();
  });

  it('muestra el badge de variación en historial cronológico de CDP', () => {
    render(
      <DashboardTrendChart
        tendencia={[
          { semana: '04 Nov', asistencia: 10, porcentaje: 50 },
          { semana: '11 Nov', asistencia: 20, porcentaje: 100 },
        ]}
        promedioTendencia={15}
        periodo="semana"
        nivel="cdp"
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('+100% vs anterior')).toBeInTheDocument();
  });
});
