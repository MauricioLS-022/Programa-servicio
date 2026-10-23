import React from 'react';
import type { RankingRedItem } from '../../types/estructura';

export interface DashboardRankingCardProps {
  ranking?: RankingRedItem[];
  periodo?: string;
  periodoNombre?: string;
}

export const DashboardRankingCard: React.FC<DashboardRankingCardProps> = ({
  ranking = [],
  periodo = 'semana',
  periodoNombre = '',
}) => {
  const subtitle =
    periodo === 'mes'
      ? `Cumplimiento y asistencia de ${periodoNombre || 'el mes'}`
      : periodo === 'anio'
      ? `Cumplimiento y asistencia de ${periodoNombre || 'el año'}`
      : 'Cumplimiento y asistencia de la semana';

  const items = ranking.length > 0 ? ranking : [];

  return (
    <article className="participation-card">
      <div className="status-card-header">
        <h2 className="section-title">Ranking de Redes</h2>
        <p className="section-subtitle">{subtitle}</p>
      </div>

      <div className="network-ranking-list">
        {items.length > 0 ? (
          items.map((redItem, idx) => {
            const pos = idx + 1;
            const cumpl = redItem.cumplimiento || 0;
            const asist = redItem.asistencia || redItem.asistencia_semana || 0;
            const colorCls = redItem.color_class || 'default';

            return (
              <div key={`${redItem.nombre}-${idx}`} className={`ranking-item podium-${pos}`}>
                <div className="ranking-row">
                  <div className="ranking-name-box" title={`${redItem.nombre} (Supervisor: ${redItem.supervisor})`}>
                    <span className={`ranking-pos pos-${pos}`} title={`Puesto #${pos} del podio ministerial`}>
                      #{pos}
                    </span>
                    <strong title={redItem.nombre}>{redItem.nombre}</strong>
                    <span className="ranking-sup" title={`Supervisor: ${redItem.supervisor}`}>({redItem.supervisor})</span>
                  </div>
                  <div className="ranking-stats">
                    <span className="ranking-asist" title={`${asist} asistentes esta semana`}>{asist} asists.</span>
                    <span className="ranking-percent" title={`${cumpl}% de reporte de Casas de Paz`}>{cumpl}% cumpl.</span>
                  </div>
                </div>
                <div
                  className="progress-bar"
                  title={`${redItem.casas_reportadas || 0} de ${redItem.total_casas || 0} Casas de Paz con reporte (${cumpl}%)`}
                >
                  <div
                    className={`progress-fill fill-${colorCls}`}
                    style={{
                      width: `${cumpl}%`,
                      ['--bar-width' as string]: `${cumpl}%`,
                    }}
                  />
                </div>
              </div>
            );
          })
        ) : (
          <div className="empty-state">
            <span className="material-symbols-outlined empty-icon">leaderboard</span>
            <p className="empty-message">Aún no hay redes con reportes para comparar.</p>
          </div>
        )}
      </div>
    </article>
  );
};

