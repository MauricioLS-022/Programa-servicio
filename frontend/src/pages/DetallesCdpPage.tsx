import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCdpDetalle, useEstructuraMutations, useEstructuraSelectores } from '../hooks/useEstructura';
import { useAuth } from '../hooks/useAuth';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useToast } from '../context/ToastContext';
import { Button } from '../components/ui/Button';
import { CasaDePazModal } from '../components/estructura/CasaDePazModal';
import { LiderModal } from '../components/estructura/LiderModal';
import {
  Home,
  FileDown,
  PauseCircle,
  PlayCircle,
  Edit,
  ArrowLeft,
  Users,
  ClipboardList,
  DollarSign,
  Heart,
  Phone,
  MessageCircle,
  MapPin,
  CheckCircle,
  AlertCircle,
  Loader2,
  Calendar,
  AlertTriangle,
  UserPlus,
  Sparkles,
} from 'lucide-react';
import type { CdpInput, LiderInput } from '../types/estructura';
import '../styles/detalles_cdp.css';

export const DetallesCdpPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { success, error } = useToast();
  const isAdmin = user?.rol === 'admin';

  const { cdp, isLoading, isError, refetch } = useCdpDetalle(id);
  useDocumentTitle(cdp?.codigo ? `Casa de Paz ${cdp.codigo}` : 'Detalles Casa de Paz');
  const { selectores } = useEstructuraSelectores(id);
  const {
    toggleCdp,
    isTogglingCdp,
    editarCdp,
    isEditandoCdp,
    crearLider,
    isCreandoLider,
    editarLider,
    isEditandoLider,
  } = useEstructuraMutations();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isLiderModalOpen, setIsLiderModalOpen] = useState(false);
  const [selectedLider, setSelectedLider] = useState<any>(null);

  // Exportar Ficha Técnica a PDF (Paridad con static/scripts/admin/detalles_cdp.js)
  const handleExportPDF = () => {
    if (!cdp) return;

    try {
      const today = new Date().toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });

      const oldIframe = document.getElementById('print-cdp-iframe');
      if (oldIframe) oldIframe.remove();

      const printIframe = document.createElement('iframe');
      printIframe.id = 'print-cdp-iframe';
      printIframe.style.position = 'fixed';
      printIframe.style.right = '0';
      printIframe.style.bottom = '0';
      printIframe.style.width = '0';
      printIframe.style.height = '0';
      printIframe.style.border = '0';
      printIframe.style.visibility = 'hidden';
      document.body.appendChild(printIframe);

      const teamRows = (cdp.lideres || [])
        .map(
          (m) => `
          <tr>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${m.nombre_completo}</strong></td>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">${m.rol}</td>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">${m.telefono || 'No registrado'}</td>
          </tr>`
        )
        .join('');

      const reportRows = (cdp.reportes || [])
        .map(
          (r) => `
          <tr>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${r.fecha_formateada || r.fecha || ''}</strong></td>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">
              <strong>${r.tema || 'Sin tema registrado'}</strong>
              ${r.observaciones ? `<div style="font-size: 10px; color: #666; margin-top: 2px;">${r.observaciones}</div>` : ''}
            </td>
            <td style="text-align: center; padding: 6px 8px; border-bottom: 1px solid #eee;"><strong>${r.asistencia || 0}</strong></td>
            <td style="font-size: 11px; padding: 6px 8px; border-bottom: 1px solid #eee;">Reg: ${r.nro_regulares || 0} · Niñ: ${r.nro_ninos || r.nro_niños || 0} · Vis: ${r.nro_visitas || 0}</td>
            <td style="padding: 6px 8px; border-bottom: 1px solid #eee;">$${Number(r.ofrendas_usd || 0).toFixed(2)} · Bs. ${Number(r.ofrendas_bs || 0).toFixed(2)}</td>
            <td style="text-align: center; padding: 6px 8px; border-bottom: 1px solid #eee;">${r.cesta_amor ? 'Sí' : 'No'}</td>
          </tr>`
        )
        .join('');

      const html = `
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <meta charset="UTF-8">
          <title>Ficha Técnica Oficial - Casa de Paz ${cdp.codigo}</title>
          <style>
            @page { size: letter portrait; margin: 12mm 15mm; }
            * { box-sizing: border-box; }
            body {
              font-family: 'Segoe UI', Arial, -apple-system, sans-serif;
              color: #2b1111;
              background: #ffffff;
              padding: 15px;
              margin: 0;
              font-size: 12px;
              line-height: 1.4;
            }
            .doc-header {
              border-bottom: 2.5px solid #390002;
              padding-bottom: 12px;
              margin-bottom: 16px;
              display: flex;
              justify-content: space-between;
              align-items: flex-end;
            }
            .brand-title {
              font-size: 22px;
              font-weight: 800;
              color: #390002;
              margin: 0 0 2px 0;
            }
            .brand-subtitle {
              font-size: 12px;
              color: #564240;
              text-transform: uppercase;
              letter-spacing: 0.08em;
              font-weight: 600;
            }
            .section-title {
              font-size: 13px;
              font-weight: 700;
              color: #390002;
              text-transform: uppercase;
              letter-spacing: 0.05em;
              border-bottom: 1px solid #e8d0cc;
              padding-bottom: 4px;
              margin: 14px 0 8px 0;
            }
            .kpi-container {
              display: flex;
              gap: 8px;
              margin-bottom: 14px;
            }
            .kpi-box {
              flex: 1;
              background: #faf5f3;
              border: 1px solid #e8d0cc;
              border-radius: 6px;
              padding: 8px 10px;
              text-align: center;
            }
            .kpi-label { font-size: 9.5px; text-transform: uppercase; font-weight: 700; color: #5a4240; }
            .kpi-val { font-size: 16px; font-weight: 800; color: #390002; margin: 3px 0; }
            .kpi-sub { font-size: 9.5px; color: #700204; font-weight: 600; }
            table { width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 12px; }
            th {
              background-color: #f8e4e3;
              color: #390002;
              font-weight: 700;
              text-align: left;
              padding: 6px 8px;
              border-bottom: 1.5px solid #ddc0bd;
              font-size: 10px;
              text-transform: uppercase;
            }
          </style>
        </head>
        <body>
          <div class="doc-header">
            <div>
              <div class="brand-title">Comunidad Cristiana Vino Nuevo</div>
              <div class="brand-subtitle">Ficha Técnica Oficial · Casa "${cdp.codigo}"</div>
            </div>
            <div style="text-align: right; font-size: 11px;">
              <div>Emisión: ${today}</div>
              <div>Red: <strong>${cdp.red_nombre}</strong> · Supervisor: <strong>${cdp.supervisor_nombre}</strong></div>
            </div>
          </div>

          <div class="section-title">1. Resumen de Desempeño y Crecimiento</div>
          <div class="kpi-container">
            <div class="kpi-box">
              <div class="kpi-label">Asistencia Prom.</div>
              <div class="kpi-val">${cdp.asistencia_promedio}</div>
              <div class="kpi-sub">personas / reunión</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Reportes Totales</div>
              <div class="kpi-val">${cdp.total_reportes}</div>
              <div class="kpi-sub">semanas reportadas</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Ofrendas Totales</div>
              <div class="kpi-val">$${Number(cdp.ofrendas_usd_totales || 0).toFixed(2)}</div>
              <div class="kpi-sub">Bs. ${Number(cdp.ofrendas_bs_totales || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Visitas & Conversiones</div>
              <div class="kpi-val">${cdp.visitas_totales}</div>
              <div class="kpi-sub">${cdp.conversiones_totales} conversiones</div>
            </div>
          </div>

          <div class="section-title">2. Información del Centro</div>
          <table>
            <tr>
              <td style="width: 25%; font-weight: bold; padding: 4px 6px;">Dirección:</td>
              <td style="width: 25%; padding: 4px 6px;">${cdp.direccion || 'No registrada'}</td>
              <td style="width: 25%; font-weight: bold; padding: 4px 6px;">Anfitrión:</td>
              <td style="width: 25%; padding: 4px 6px;">${cdp.anfitrion || 'Sin asignar'}</td>
            </tr>
            <tr>
              <td style="font-weight: bold; padding: 4px 6px;">Teléfono:</td>
              <td style="padding: 4px 6px;">${cdp.telefono || 'No registrado'}</td>
              <td style="font-weight: bold; padding: 4px 6px;">Horario:</td>
              <td style="padding: 4px 6px;">${cdp.horario || 'Miércoles · 7:00 PM'}</td>
            </tr>
          </table>

          <div class="section-title">3. Equipo de Liderazgo Responsable</div>
          <table>
            <thead>
              <tr>
                <th style="width: 45%;">Nombre Completo</th>
                <th style="width: 30%;">Rol</th>
                <th style="width: 25%;">Teléfono</th>
              </tr>
            </thead>
            <tbody>
              ${teamRows || '<tr><td colspan="3" style="text-align: center; padding: 8px;">No hay líderes asignados.</td></tr>'}
            </tbody>
          </table>

          <div class="section-title">4. Historial Reciente de Reportes</div>
          <table>
            <thead>
              <tr>
                <th style="width: 14%;">Fecha</th>
                <th style="width: 34%;">Tema</th>
                <th style="width: 12%; text-align: center;">Asistencia</th>
                <th style="width: 20%;">Desglose</th>
                <th style="width: 12%;">Ofrendas</th>
                <th style="width: 8%; text-align: center;">Cesta</th>
              </tr>
            </thead>
            <tbody>
              ${reportRows || '<tr><td colspan="6" style="text-align: center; padding: 8px;">Sin reportes registrados aún.</td></tr>'}
            </tbody>
          </table>
        </body>
        </html>
      `;

      const frameDoc = printIframe.contentWindow?.document;
      if (frameDoc) {
        frameDoc.open();
        frameDoc.write(html);
        frameDoc.close();
        setTimeout(() => {
          printIframe.contentWindow?.focus();
          printIframe.contentWindow?.print();
        }, 300);
      }
    } catch (err) {
      console.error('Error exportando PDF:', err);
      window.print();
    }
  };

  const handleToggleEstado = async () => {
    if (!cdp) return;
    try {
      const res = await toggleCdp(cdp.id);
      if (res.success) {
        success(res.message || 'Estado de la Casa de Paz actualizado.');
        refetch();
      } else {
        error(res.message || 'Error al cambiar estado.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const handleGuardarEdicion = async (data: CdpInput) => {
    if (!cdp) return;
    try {
      const res = await editarCdp({ id: cdp.id, data });
      if (res.success) {
        success('¡Casa de Paz actualizada exitosamente!');
        refetch();
      } else {
        error(res.message || 'Error al actualizar Casa de Paz.');
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  const handleAbrirCrearLider = () => {
    setSelectedLider(null);
    setIsLiderModalOpen(true);
  };

  const handleAbrirEditarLider = (miembro: any) => {
    setSelectedLider(miembro);
    setIsLiderModalOpen(true);
  };

  const handleGuardarLider = async (data: LiderInput) => {
    if (!cdp) return;
    try {
      if (selectedLider?.id) {
        const res = await editarLider({ id: selectedLider.id, data });
        if (res.success) {
          success(res.message || 'Líder actualizado exitosamente.');
          refetch();
        } else {
          error(res.message || 'Error al actualizar líder.');
        }
      } else {
        const res = await crearLider(data);
        if (res.success) {
          success(res.message || 'Líder asignado exitosamente.');
          refetch();
        } else {
          error(res.message || 'Error al asignar líder.');
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) error(err.message);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 text-vino dark:text-vino-light animate-spin" />
        <p className="text-sm font-medium text-text-muted dark:text-neutral-400">
          Cargando Ficha Técnica de la Casa de Paz...
        </p>
      </div>
    );
  }

  if (isError || !cdp) {
    return (
      <div className="py-16 text-center max-w-md mx-auto flex flex-col items-center gap-4">
        <AlertTriangle className="w-12 h-12 text-amber-600" />
        <h2 className="text-lg font-bold text-text-main dark:text-neutral-100">
          No se pudo cargar la Casa de Paz
        </h2>
        <p className="text-xs text-text-muted dark:text-neutral-400">
          Es posible que la entidad haya sido reubicada o el backend esté temporalmente en modo degradado.
        </p>
        <div className="flex items-center gap-3 mt-2">
          <Button variant="outline" onClick={() => refetch()}>
            Reintentar
          </Button>
          <Link to="/estructura">
            <Button variant="primary">Volver a Estructura</Button>
          </Link>
        </div>
      </div>
    );
  }

  const cleanPhone = (cdp.telefono || '').replace(/[^0-9]/g, '');
  const isActive = Boolean(cdp.is_active);

  return (
    <div className="detalles-cdp-wrapper">
      {/* Header Institucional */}
      <header className="detail-header">
        <div className="detail-title-group">
          <div className="detail-icon-badge" aria-hidden="true">
            <Home className="w-6 h-6" />
          </div>
          <div>
            <p className="detail-eyebrow">Ficha Informativa · Casa de Paz</p>
            <h1 className="detail-title">Casa "{cdp.codigo || cdp.nombre}"</h1>
            <p className="detail-subtitle">
              <span className="badge-network">{cdp.red_nombre}</span>
              <span>· Supervisor: <strong>{cdp.supervisor_nombre || 'Sin asignar'}</strong></span>
            </p>
          </div>
        </div>

        <div className="detail-actions">
          <button
            type="button"
            onClick={handleExportPDF}
            className="btn-secondary"
            aria-label="Exportar Ficha Técnica de Casa de Paz en PDF"
          >
            <FileDown className="w-4 h-4" />
            <span>Exportar PDF</span>
          </button>

          {isAdmin && (
            <>
              <button
                type="button"
                onClick={handleToggleEstado}
                disabled={isTogglingCdp}
                className="btn-secondary"
              >
                {isActive ? (
                  <>
                    <PauseCircle className="w-4 h-4" />
                    <span>Pausar Casa</span>
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4" />
                    <span>Reactivar Casa</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => setIsEditModalOpen(true)}
                className="btn-secondary"
              >
                <Edit className="w-4 h-4" />
                <span>Editar</span>
              </button>
            </>
          )}

          <Link to="/estructura" className="btn-secondary">
            <ArrowLeft className="w-4 h-4" />
            <span>Volver</span>
          </Link>
        </div>
      </header>

      {/* Métricas Clave (KPIs Balanceados: 6 indicadores) */}
      <section className="metrics-grid" aria-label="Métricas clave de la Casa de Paz">
        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            <Users className="w-5 h-5" />
          </div>
          <div className="metric-data">
            <span className="metric-label">Asistencia Prom.</span>
            <strong className="metric-value">{cdp.asistencia_promedio || 0}</strong>
            <span className="metric-subtext">Personas / reunión</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            <ClipboardList className="w-5 h-5" />
          </div>
          <div className="metric-data">
            <span className="metric-label">Reportes</span>
            <strong className="metric-value">{cdp.total_reportes || 0}</strong>
            <span className="metric-subtext">Semanas reportadas</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            <DollarSign className="w-5 h-5" />
          </div>
          <div className="metric-data">
            <span className="metric-label">Ofrendas Totales</span>
            <strong className="metric-value">
              ${Number(cdp.ofrendas_usd_totales || 0).toFixed(2)}
            </strong>
            <span className="metric-subtext">
              Bs. {Number(cdp.ofrendas_bs_totales || 0).toFixed(2)}
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            <Heart className="w-5 h-5" />
          </div>
          <div className="metric-data">
            <span className="metric-label">Visitas</span>
            <strong className="metric-value">{cdp.visitas_totales || 0}</strong>
            <span className="metric-subtext">Nuevas personas</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="metric-data">
            <span className="metric-label">Fruto Espiritual</span>
            <strong className="metric-value">
              {(cdp.conversiones_totales || 0) + (cdp.reconciliaciones_totales || 0)}
            </strong>
            <span className="metric-subtext">
              {cdp.conversiones_totales || 0} conv. · {cdp.reconciliaciones_totales || 0} reconc.
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" aria-hidden="true">
            {!isActive ? (
              <PauseCircle className="w-5 h-5 text-neutral-500" />
            ) : cdp.reporte_reciente_7d || cdp.estado_reporte_7d === 'al_dia' ? (
              <CheckCircle className="w-5 h-5 text-emerald-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-amber-600" />
            )}
          </div>
          <div className="metric-data">
            <span className="metric-label">Pulso Semanal</span>
            <strong className="metric-value">
              {!isActive
                ? 'Pausada'
                : cdp.reporte_reciente_7d || cdp.estado_reporte_7d === 'al_dia'
                ? 'Al día'
                : 'Pendiente'}
            </strong>
            <span className="metric-subtext">
              {cdp.dias_desde_ultimo_reporte !== null && cdp.dias_desde_ultimo_reporte !== undefined
                ? `Hace ${cdp.dias_desde_ultimo_reporte} d`
                : !isActive
                ? 'Casa en pausa'
                : 'Sin reportes'}
            </span>
          </div>
        </div>
      </section>

      {/* Grilla Principal */}
      <div className="detail-grid">
        {/* Tarjeta: Datos Principales & Contacto */}
        <section className="detail-card">
          <div className="card-header">
            <div>
              <p className="card-kicker">Datos Principales</p>
              <h2>Información del Centro</h2>
            </div>
            <span className={`status-pill ${isActive ? 'active' : 'inactiva'}`}>
              {isActive ? 'Activa' : 'Inactiva / Pausada'}
            </span>
          </div>

          <div className="info-grid">
            <div className="info-item">
              <div className="info-meta">
                <span className="info-label">Dirección</span>
                <span className="info-value">{cdp.direccion || 'Sin dirección registrada'}</span>
              </div>
              {cdp.maps_url && (
                <a
                  href={cdp.maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-action-icon"
                  title="Abrir en Google Maps"
                >
                  <MapPin className="w-4 h-4 text-vino dark:text-vino-light" />
                </a>
              )}
            </div>

            <div className="info-item">
              <div className="info-meta">
                <span className="info-label">Anfitrión</span>
                <span className="info-value">{cdp.anfitrion || 'Sin anfitrión asignado'}</span>
              </div>
            </div>

            <div className="info-item">
              <div className="info-meta">
                <span className="info-label">Teléfono de la Casa</span>
                <span className="info-value">{cdp.telefono || 'No registrado'}</span>
              </div>
              {cdp.telefono && cdp.telefono !== 'No registrado' && (
                <div className="flex items-center gap-1.5">
                  <a
                    href={`https://wa.me/${cleanPhone}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-action-icon btn-wa"
                    title="WhatsApp"
                  >
                    <MessageCircle className="w-4 h-4" />
                  </a>
                  <a
                    href={`tel:${cleanPhone}`}
                    className="btn-action-icon"
                    title="Llamar"
                  >
                    <Phone className="w-4 h-4" />
                  </a>
                </div>
              )}
            </div>

            <div className="info-item">
              <div className="info-meta">
                <span className="info-label">Horario de Reunión</span>
                <span className="info-value">{cdp.horario || 'Miércoles · 7:00 PM'}</span>
              </div>
            </div>

            <div className="info-item full-width">
              <div className="info-meta">
                <span className="info-label">Usuario del Sistema</span>
                <span className="info-value">
                  {cdp.usuario_username ? (
                    <>
                      <strong>@{cdp.usuario_username}</strong>
                      {cdp.usuario_nombre && (
                        <span className="text-text-muted text-xs ml-1.5">
                          ({cdp.usuario_nombre} {cdp.usuario_apellido})
                        </span>
                      )}
                    </>
                  ) : (
                    'Sin cuenta vinculada'
                  )}
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Tarjeta: Equipo de Liderazgo Responsable */}
        <section className="detail-card">
          <div className="card-header">
            <div>
              <p className="card-kicker">Equipo</p>
              <h2>Responsables Asignados</h2>
            </div>
            <div className="card-header-actions">
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-surface-sidebar dark:bg-neutral-800 text-text-muted border border-border-subtle">
                {cdp.lideres?.length || 0} líderes
              </span>
              {isAdmin && (
                <button
                  type="button"
                  onClick={handleAbrirCrearLider}
                  className="btn-add-team-member"
                  title="Añadir líder a la Casa de Paz"
                  aria-label="Añadir líder a la Casa de Paz"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Añadir</span>
                </button>
              )}
            </div>
          </div>

          <div className="team-list">
            {cdp.lideres && cdp.lideres.length > 0 ? (
              cdp.lideres.map((m) => {
                const memberPhone = (m.telefono || '').replace(/[^0-9]/g, '');
                return (
                  <div key={m.id} className="team-member">
                    <div className="avatar" aria-hidden="true">
                      {m.iniciales || 'L'}
                    </div>
                    <div className="team-member-info">
                      <strong>{m.nombre_completo}</strong>
                      <p>{m.rol}</p>
                      {m.telefono && <span className="text-xs text-text-muted">{m.telefono}</span>}
                    </div>
                    <div className="team-member-actions">
                      {m.telefono && (
                        <>
                          <a
                            href={`https://wa.me/${memberPhone}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-action-icon btn-wa"
                            title={`WhatsApp a ${m.nombre_completo}`}
                          >
                            <MessageCircle className="w-4 h-4" />
                          </a>
                          <a
                            href={`tel:${memberPhone}`}
                            className="btn-action-icon"
                            title={`Llamar a ${m.nombre_completo}`}
                          >
                            <Phone className="w-4 h-4" />
                          </a>
                        </>
                      )}
                      {isAdmin && (
                        <button
                          type="button"
                          onClick={() => handleAbrirEditarLider(m)}
                          className="btn-action-icon"
                          title={`Editar o reasignar a ${m.nombre_completo}`}
                        >
                          <Edit className="w-3.5 h-3.5 text-text-muted hover:text-vino" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="py-8 text-center flex flex-col items-center justify-center gap-2">
                <p className="text-xs text-text-muted dark:text-neutral-400">
                  No hay líderes asignados a esta Casa de Paz.
                </p>
                {isAdmin && (
                  <Button variant="outline" size="sm" onClick={handleAbrirCrearLider}>
                    <UserPlus className="w-3.5 h-3.5 mr-1.5" />
                    Añadir primer líder
                  </Button>
                )}
              </div>
            )}
          </div>
        </section>

        {/* Tarjeta Ancha: Historial Reciente de Reportes */}
        <section className="detail-card reports-card">
          <div className="card-header">
            <div>
              <p className="card-kicker">Historial Reciente</p>
              <h2>Últimos Reportes Semanales</h2>
            </div>
          </div>

          {cdp.reportes && cdp.reportes.length > 0 ? (
            <div className="reports-table-responsive">
              <table className="reports-table" aria-label="Tabla de reportes semanales registrados">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Tema de la Reunión</th>
                    <th>Asistencia</th>
                    <th>Desglose</th>
                    <th>Ofrenda</th>
                    <th>Cesta</th>
                  </tr>
                </thead>
                <tbody>
                  {cdp.reportes.slice(0, 5).map((rep, idx) => (
                    <tr key={rep.id || idx}>
                      <td>
                        <div className="flex items-center gap-1.5 font-bold">
                          <Calendar className="w-3.5 h-3.5 text-vino dark:text-vino-light" />
                          <span>{rep.fecha_formateada || rep.fecha}</span>
                        </div>
                      </td>
                      <td>
                        <strong>{rep.tema || 'Sin tema registrado'}</strong>
                        {rep.observaciones && (
                          <p className="text-[11px] text-text-muted truncate max-w-xs mt-0.5" title={rep.observaciones}>
                            {rep.observaciones}
                          </p>
                        )}
                      </td>
                      <td>
                        <span className="total-attendance-pill">{rep.asistencia || 0} pers.</span>
                      </td>
                      <td>
                        <div className="breakdown-tags">
                          <span>Reg: {rep.nro_regulares || 0}</span>
                          <span>Niñ: {rep.nro_ninos || rep.nro_niños || 0}</span>
                          <span>Vis: {rep.nro_visitas || 0}</span>
                        </div>
                      </td>
                      <td>
                        <div className="text-xs font-semibold">
                          {rep.ofrendas_usd ? `$${Number(rep.ofrendas_usd).toFixed(2)}` : ''}
                          {rep.ofrendas_bs ? ` · Bs. ${Number(rep.ofrendas_bs).toFixed(2)}` : ''}
                          {!rep.ofrendas_usd && !rep.ofrendas_bs && '$0.00'}
                        </div>
                      </td>
                      <td>
                        {rep.cesta_amor ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 dark:text-emerald-300">
                            <CheckCircle className="w-3.5 h-3.5" /> Sí
                          </span>
                        ) : (
                          <span className="text-[11px] text-text-muted">No</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-text-muted dark:text-neutral-400">
              No se han registrado reportes aún para esta Casa de Paz.
            </div>
          )}
        </section>
      </div>

      {/* Modal de Edición de Casa de Paz */}
      {isEditModalOpen && (
        <CasaDePazModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          casa={cdp}
          redes={selectores?.redes || []}
          lideresDisponibles={selectores?.lideres_cdp || []}
          onSave={handleGuardarEdicion}
          isSaving={isEditandoCdp}
        />
      )}

      {/* Modal de Asignación / Edición de Líder */}
      {isLiderModalOpen && (
        <LiderModal
          isOpen={isLiderModalOpen}
          onClose={() => {
            setIsLiderModalOpen(false);
            setSelectedLider(null);
          }}
          lider={selectedLider}
          cdpId={cdp.id}
          cdpCodigo={cdp.codigo}
          onSave={handleGuardarLider}
          isSaving={isCreandoLider || isEditandoLider}
        />
      )}
    </div>
  );
};
