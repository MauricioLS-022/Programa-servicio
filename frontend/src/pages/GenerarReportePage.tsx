import React from 'react';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useGenerarReporteForm } from '../hooks/useGenerarReporteForm';
import { Icon } from '../components/ui/Icon';
import '../styles/generar_reporte.css';

export const GenerarReportePage: React.FC = () => {
  useDocumentTitle('Generar Reporte');

  const {
    user,
    isCreando,
    sinCdpAsignada,
    casas,
    lideres,
    cdpInfo,
    returnUrl,
    navigate,
    selectedCdpId,
    setSelectedCdpId,
    liderId,
    setLiderId,
    fecha,
    hrInicio,
    setHrInicio,
    hrFin,
    setHrFin,
    nroRegulares,
    setNroRegulares,
    nroNinos,
    setNroNinos,
    nroVisitas,
    setNroVisitas,
    nroComprometidos,
    setNroComprometidos,
    reconciliaciones,
    setReconciliaciones,
    confesiones,
    setConfesiones,
    ofrendasBs,
    setOfrendasBs,
    ofrendasUsd,
    setOfrendasUsd,
    cestaAmor,
    setCestaAmor,
    tema,
    setTema,
    observaciones,
    setObservaciones,
    totalAsistencia,
    handleSubmit,
  } = useGenerarReporteForm();

  // Candado institucional: Líder de Casa de Paz sin CDP asignada
  if (sinCdpAsignada) {
    return (
      <div className="generar-reporte-wrapper">
        <main className="crud-container report-container">
          <header className="report-header">
            <div>
              <h1 className="form-title">Generar Reporte</h1>
              <p className="form-description">
                Registra los datos y estadísticas de la reunión semanal de tu Casa de Paz.
              </p>
            </div>
          </header>

          <div
            className="report-form"
            style={{
              textAlign: 'center',
              padding: '3rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '1rem',
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                backgroundColor: 'rgba(120, 2, 4, 0.08)',
                color: 'var(--color1, #4A0203)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Icon name="home" size={32} />
            </div>
            <h2
              style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                color: 'var(--color1, #4A0203)',
                margin: 0,
              }}
            >
              Sin Casa de Paz Asignada
            </h2>
            <p
              style={{
                maxWidth: '440px',
                fontSize: '0.875rem',
                color: 'var(--text-muted, #725555)',
                lineHeight: 1.5,
                margin: 0,
              }}
            >
              Tu cuenta de líder ministerial aún no tiene una Casa de Paz vinculada en el sistema.
              Contacta a tu supervisor de Red para que realice la asignación antes de poder registrar reportes semanales.
            </p>
            <button
              type="button"
              className="btn-save"
              onClick={() => navigate('/dashboard')}
              style={{ marginTop: '0.5rem' }}
            >
              <Icon name="arrow_back" size={18} />
              <span>Volver al Dashboard</span>
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="generar-reporte-wrapper">
      <main className="crud-container report-container">
        {/* Encabezado con Contexto de Casa de Paz */}
        <header className="report-header">
          <div>
            <h1 className="form-title">Generar Reporte</h1>
            <p className="form-description">
              Registra los datos y estadísticas de la reunión semanal de tu Casa de Paz.
            </p>
          </div>
          {cdpInfo && (
            <div className="cdp-context-badge" title="Casa de Paz vinculada">
              <Icon name="home" size={18} />
              <span>
                <strong>{cdpInfo.codigo}</strong> · {cdpInfo.nombre}
              </span>
            </div>
          )}
        </header>

        <form className="crud-form report-form" onSubmit={handleSubmit} noValidate>
          {/* Selector de Casa de Paz para Administradores */}
          {user?.rol === 'admin' && (
            <div className="form-group compact" style={{ marginBottom: '1rem' }}>
              <label htmlFor="admin_cdp_select">
                Casa de Paz asignada <span style={{ color: 'var(--color2)' }}>*</span>
              </label>
              <div className="input-wrapper icon-left">
                <span className="input-icon">
                  <Icon name="home" size={18} />
                </span>
                <select
                  id="admin_cdp_select"
                  value={selectedCdpId || ''}
                  onChange={(e) => setSelectedCdpId(e.target.value ? Number(e.target.value) : undefined)}
                  required
                >
                  <option value="">Selecciona la Casa de Paz a reportar...</option>
                  {casas.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.codigo} · {c.nombre || c.anfitrion || `Casa #${c.id}`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* SECCIÓN 1: DATOS DE LA REUNIÓN Y HORARIO */}
          <section className="form-section-card">
            <div className="section-card-header">
              <div className="section-card-title">
                <Icon name="event_available" size={20} className="icon-svg" />
                <span>Datos de la Reunión</span>
              </div>
            </div>

            <div className="grid-row grid-1-col" style={{ marginBottom: '0.75rem' }}>
              <div className="form-group compact">
                <label htmlFor="lider_id">Líder que reporta</label>
                <div className="input-wrapper icon-left">
                  <span className="input-icon">
                    <Icon name="badge" size={18} />
                  </span>
                  <select
                    id="lider_id"
                    name="lider_id"
                    value={liderId}
                    onChange={(e) => setLiderId(e.target.value)}
                  >
                    <option value="">Selecciona el líder encargado (Opcional)...</option>
                    {lideres.map((lider) => (
                      <option key={lider.id} value={lider.id}>
                        {lider.nombre} {lider.apellido || ''} {lider.rol ? `(${lider.rol})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="grid-row grid-3-col">
              <div className="form-group compact">
                <label htmlFor="fecha">Fecha (Hoy)</label>
                <div className="input-wrapper icon-left">
                  <span className="input-icon">
                    <Icon name="calendar_today" size={18} />
                  </span>
                  <input
                    type="date"
                    id="fecha"
                    name="fecha"
                    value={fecha}
                    readOnly
                    max={fecha}
                    required
                    title="La fecha del reporte se fija automáticamente al día actual."
                  />
                </div>
              </div>

              <div className="form-group compact">
                <label htmlFor="hr_inicio">Hora de inicio</label>
                <div className="input-wrapper icon-left">
                  <span className="input-icon">
                    <Icon name="schedule" size={18} />
                  </span>
                  <input
                    type="time"
                    id="hr_inicio"
                    name="hr_inicio"
                    value={hrInicio}
                    onChange={(e) => setHrInicio(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="form-group compact">
                <label htmlFor="hr_fin">Hora de finalización</label>
                <div className="input-wrapper icon-left">
                  <span className="input-icon">
                    <Icon name="schedule" size={18} />
                  </span>
                  <input
                    type="time"
                    id="hr_fin"
                    name="hr_fin"
                    value={hrFin}
                    onChange={(e) => setHrFin(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>
          </section>

          {/* SECCIÓN 2: ASISTENCIA Y MÉTRICAS */}
          <section className="form-section-card">
            <div className="section-card-header">
              <div className="section-card-title">
                <Icon name="group" size={20} className="icon-svg" />
                <span>Asistencia</span>
              </div>
              <div className="attendance-live-badge" title="Suma total de asistentes">
                <span>Total:</span>
                <span id="badge-total-asistencia" className="badge-number">
                  {totalAsistencia}
                </span>
              </div>
            </div>

            <div className="grid-asistencia">
              <div className="metric-input-card">
                <div className="metric-header">
                  <Icon name="groups" size={18} />
                  <label htmlFor="nro_regulares">Regulares</label>
                </div>
                <input
                  type="number"
                  id="nro_regulares"
                  name="nro_regulares"
                  className="attendance-counter"
                  placeholder="0"
                  min="0"
                  value={nroRegulares}
                  onChange={(e) =>
                    setNroRegulares(e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0))
                  }
                  required
                />
              </div>

              <div className="metric-input-card">
                <div className="metric-header">
                  <Icon name="child_care" size={18} />
                  <label htmlFor="nro_ninos">Niños</label>
                </div>
                <input
                  type="number"
                  id="nro_ninos"
                  name="nro_ninos"
                  className="attendance-counter"
                  placeholder="0"
                  min="0"
                  value={nroNinos}
                  onChange={(e) =>
                    setNroNinos(e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0))
                  }
                  required
                />
              </div>

              <div className="metric-input-card">
                <div className="metric-header">
                  <Icon name="person_add" size={18} />
                  <label htmlFor="nro_visitas">Visitas</label>
                </div>
                <input
                  type="number"
                  id="nro_visitas"
                  name="nro_visitas"
                  className="attendance-counter"
                  placeholder="0"
                  min="0"
                  value={nroVisitas}
                  onChange={(e) =>
                    setNroVisitas(e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0))
                  }
                  required
                />
              </div>

              <div className="metric-input-card">
                <div className="metric-header">
                  <Icon name="verified" size={18} />
                  <label htmlFor="nro_comprometidos">Comprometidos</label>
                </div>
                <input
                  type="number"
                  id="nro_comprometidos"
                  name="nro_comprometidos"
                  className="attendance-counter"
                  placeholder="0"
                  min="0"
                  value={nroComprometidos}
                  onChange={(e) =>
                    setNroComprometidos(
                      e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0)
                    )
                  }
                  required
                />
              </div>
            </div>
          </section>

          {/* SECCIÓN 3: MINISTERIO ESPIRITUAL Y FINANZAS */}
          <div className="grid-row grid-2-col" style={{ marginBottom: '0.9rem' }}>
            {/* Sub-bloque Ministerio */}
            <section className="form-section-card" style={{ marginBottom: 0 }}>
              <div className="section-card-header">
                <div className="section-card-title">
                  <Icon name="favorite" size={20} className="icon-svg" />
                  <span>Ministerio</span>
                </div>
              </div>
              <div className="grid-row grid-2-col">
                <div className="form-group compact">
                  <label htmlFor="reconciliaciones">Reconciliaciones</label>
                  <div className="input-wrapper icon-left">
                    <span className="input-icon">
                      <Icon name="favorite" size={18} />
                    </span>
                    <input
                      type="number"
                      id="reconciliaciones"
                      name="reconciliaciones"
                      placeholder="0"
                      min="0"
                      value={reconciliaciones}
                      onChange={(e) =>
                        setReconciliaciones(
                          e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0)
                        )
                      }
                    />
                  </div>
                </div>

                <div className="form-group compact">
                  <label htmlFor="confesiones">Confesiones de fe</label>
                  <div className="input-wrapper icon-left">
                    <span className="input-icon">
                      <Icon name="menu_book" size={18} />
                    </span>
                    <input
                      type="number"
                      id="confesiones"
                      name="confesiones"
                      placeholder="0"
                      min="0"
                      value={confesiones}
                      onChange={(e) =>
                        setConfesiones(
                          e.target.value === '' ? '' : Math.max(0, parseInt(e.target.value, 10) || 0)
                        )
                      }
                    />
                  </div>
                </div>
              </div>
            </section>

            {/* Sub-bloque Ofrendas y Recursos */}
            <section className="form-section-card" style={{ marginBottom: 0 }}>
              <div className="section-card-header">
                <div className="section-card-title">
                  <Icon name="volunteer_activism" size={20} className="icon-svg" />
                  <span>Ofrendas y Recursos</span>
                </div>
              </div>
              <div className="grid-row grid-3-col">
                <div className="form-group compact">
                  <label htmlFor="ofrendas_bs">Bs.</label>
                  <div className="input-wrapper icon-left">
                    <span className="input-icon">
                      <Icon name="payments" size={18} />
                    </span>
                    <input
                      type="number"
                      step="0.01"
                      id="ofrendas_bs"
                      name="ofrendas_bs"
                      placeholder="0.00"
                      min="0"
                      value={ofrendasBs}
                      onChange={(e) => setOfrendasBs(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group compact">
                  <label htmlFor="ofrendas_usd">USD ($)</label>
                  <div className="input-wrapper icon-left">
                    <span className="input-icon">
                      <Icon name="attach_money" size={18} />
                    </span>
                    <input
                      type="number"
                      step="0.01"
                      id="ofrendas_usd"
                      name="ofrendas_usd"
                      placeholder="0.00"
                      min="0"
                      value={ofrendasUsd}
                      onChange={(e) => setOfrendasUsd(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-group compact">
                  <label htmlFor="cesta_amor">¿Cesta?</label>
                  <div className="input-wrapper icon-left">
                    <span className="input-icon">
                      <Icon name="description" size={18} />
                    </span>
                    <select
                      id="cesta_amor"
                      name="cesta_amor"
                      value={cestaAmor}
                      onChange={(e) => setCestaAmor(Number(e.target.value))}
                      required
                    >
                      <option value={0}>No</option>
                      <option value={1}>Sí</option>
                    </select>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* SECCIÓN 4: TEMA Y OBSERVACIONES */}
          <section className="form-section-card">
            <div className="section-card-header">
              <div className="section-card-title">
                <Icon name="notes" size={20} className="icon-svg" />
                <span>Tema y Observaciones</span>
              </div>
            </div>
            <div className="grid-row grid-1-col" style={{ gap: '0.75rem' }}>
              <div className="form-group compact">
                <label htmlFor="tema">Tema de la clase</label>
                <div className="input-wrapper icon-left">
                  <span className="input-icon">
                    <Icon name="description" size={18} />
                  </span>
                  <input
                    type="text"
                    id="tema"
                    name="tema"
                    placeholder="Ej. El poder del perdón"
                    value={tema}
                    onChange={(e) => setTema(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="form-group compact">
                <label
                  htmlFor="observaciones"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}
                >
                  <Icon name="edit_note" size={18} className="label-inline-icon" />
                  <span>Observaciones</span>
                </label>
                <textarea
                  id="observaciones"
                  name="observaciones"
                  rows={2}
                  placeholder="Escribe aquí cualquier eventualidad, petición o testimonio relevante..."
                  value={observaciones}
                  onChange={(e) => setObservaciones(e.target.value)}
                />
              </div>
            </div>
          </section>

          {/* ACCIONES */}
          <div className="report-actions">
            <div className="actions-group">
              <button
                type="submit"
                className="btn-save"
                disabled={isCreando}
                title={isCreando ? 'Enviando reporte...' : 'Guardar y enviar reporte ministerial'}
              >
                <Icon name="send" size={18} />
                <span>{isCreando ? 'Enviando Reporte...' : 'Enviar Reporte'}</span>
              </button>
              <button
                type="button"
                className="btn-cancel"
                onClick={() => navigate(returnUrl)}
              >
                Cancelar
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};
