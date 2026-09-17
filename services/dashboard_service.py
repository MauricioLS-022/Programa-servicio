"""
Servicio de dashboard - Lógica de negocio para métricas del dashboard.
Maneja la obtención y filtrado de métricas para Admin y Supervisor.
"""
from flask import current_app, session, request
from database import get_db_connection
from db_queries import formatear_horario_cdp, get_metricas_generales, get_metricas_red, get_metricas_cdp
from mock_data import (
    get_redes_demo, get_casas_demo,
    get_mock_generales, get_mock_red, get_mock_cdp,
    get_empty_generales, get_empty_red, get_empty_cdp,
)
from utils.cache import get_cached_value, set_cached_value


def mock_mode_enabled():
    """Indica si los datos demo están explícitamente habilitados."""
    try:
        from database import is_mock_mode
        return is_mock_mode()
    except Exception:
        return bool(current_app.config.get('MOCK_MODE', False))


def sanitize_metricas(metricas):
    """
    Asegura que todas las claves requeridas por el template existan en metricas.
    Agrega valores por defecto cuando los datos no están disponibles.
    """
    default_metricas = {
        # KPIs principales
        'total_asistencia': 0,
        'total_reportes': 0,
        'cumplimiento': 0,
        
        # Distribución
        'distribucion': {
            'regulares': 0,
            'ninos': 0,
            'visitas': 0,
            'comprometidos': 0,
        },
        'asistencia_ultimo': 0,
        
        # Historial
        'historial': [],
        
        # Tendencia
        'tendencia': [],
        'tendencia_semanas': [],
        
        # Rankings
        'ranking_redes': [],
        'ranking_cdp': [],
        
        # Crecimiento
        'top_crecimiento': {'nombre': 'Sin datos', 'codigo': '-', 'crecimiento': 0},
        'bottom_crecimiento': {'nombre': 'Sin datos', 'codigo': '-', 'crecimiento': 0},
        
        # CDP info
        'nombre_cdp': 'Sin asignar',
        'codigo_cdp': '-',
        'lider': 'Sin líder',
        
        # Métricas adicionales
        'conversiones': 0,
        'reconciliaciones': 0,
        'cestas_amor': 0,
        'total_visitas': 0,
        'ofrendas_usd': 0.0,
        'ofrendas_bs': 0.0,
        'casas_con_reporte': 0,
        'casas_pendientes': 0,
        'total_sin_reporte_7d': 0,
        'casas_sin_reporte_ids': [],
        'casas_sin_reporte_codigos': [],
        'lideres_red': [],
        'actividad_reciente': [],
        'ultimo_tema': 'Sin tema registrado',
        'hr_inicio': '',
        'hr_fin': '',
        'cesta_amor': False,
        'reporte_al_dia': False,
        'dias_desde_reporte': None,
        'ultimo_reporte_reciente': False,
    }
    
    # Merge con valores por defecto
    metricas_dict = metricas if isinstance(metricas, dict) else {}
    result = {**default_metricas, **metricas_dict}

    # Asegurar montos de ofrendas como float no negativo
    for f_key in ['ofrendas_usd', 'ofrendas_bs']:
        try:
            val = result.get(f_key)
            result[f_key] = max(0.0, float(val if val is not None else 0.0))
        except (ValueError, TypeError):
            result[f_key] = 0.0

    # Asegurar KPIs enteros no negativos
    int_keys = [
        'total_asistencia', 'asistencia_total', 'asistencia_ultimo', 'total_reportes',
        'cumplimiento', 'total_casas', 'casas_con_reporte', 'casas_pendientes',
        'total_sin_reporte_7d', 'conversiones', 'reconciliaciones', 'cestas_amor',
        'total_visitas', 'promedio_tendencia', 'promedio_casa', 'promedio_historico',
        'reportes_enviados', 'casas_activas'
    ]
    for i_key in int_keys:
        try:
            val = result.get(i_key)
            result[i_key] = max(0, int(val if val is not None else 0))
        except (ValueError, TypeError):
            result[i_key] = 0
    
    # Asegurar sub-diccionarios
    if 'distribucion' not in result or not isinstance(result.get('distribucion'), dict):
        result['distribucion'] = default_metricas['distribucion'].copy()
    else:
        dist = result['distribucion']
        for cat in ['regulares', 'ninos', 'visitas', 'comprometidos']:
            try:
                val = dist.get(cat)
                dist[cat] = max(0, int(val if val is not None else 0))
            except (ValueError, TypeError):
                dist[cat] = 0
    
    # Asegurar listas
    list_keys = [
        'historial', 'tendencia', 'tendencia_semanas', 'ranking_redes', 'ranking_cdp',
        'lideres_red', 'casas_sin_reporte_ids', 'casas_sin_reporte_codigos',
        'casas_sin_reporte_7d', 'alertas', 'alertas_zonal', 'casas', 'mini_historico',
        'actividad_reciente'
    ]
    for key in list_keys:
        if key not in result or not isinstance(result.get(key), list):
            result[key] = []
    
    # Sincronizar alias de tendencia y restringir a últimas 8 semanas
    raw_tend = result['tendencia_semanas'] if result['tendencia_semanas'] else result['tendencia']
    clean_tendencia = []
    for t in raw_tend:
        if isinstance(t, dict):
            try:
                asist = max(0, int(t.get('asistencia', 0) if t.get('asistencia') is not None else 0))
            except (ValueError, TypeError):
                asist = 0
            
            clean_item = {
                'semana': str(t.get('semana') or 'Semana'),
                'fecha_completa': str(t.get('fecha_completa') or t.get('semana') or ''),
                'asistencia': asist,
            }
            if 'porcentaje' in t and t.get('porcentaje') is not None:
                try:
                    clean_item['porcentaje'] = min(100, max(0, int(t['porcentaje'])))
                except (ValueError, TypeError):
                    clean_item['porcentaje'] = None
            else:
                clean_item['porcentaje'] = None
            clean_tendencia.append(clean_item)

    clean_tendencia = clean_tendencia[-8:]
    max_t_asist = max((t['asistencia'] for t in clean_tendencia), default=0)
    for t in clean_tendencia:
        if max_t_asist == 0 or t['asistencia'] == 0:
            t['porcentaje'] = 0
        else:
            t['porcentaje'] = round(t['asistencia'] / max_t_asist * 100)

    result['tendencia_semanas'] = clean_tendencia
    result['tendencia'] = clean_tendencia

    if not result.get('promedio_tendencia'):
        asists = [t['asistencia'] for t in clean_tendencia]
        result['promedio_tendencia'] = round(sum(asists) / len(asists)) if asists else 0

    # Sincronizar total_asistencia y asistencia_total entre niveles
    tot_asist = result.get('total_asistencia', 0)
    asist_tot = result.get('asistencia_total', 0)
    asist_ult = result.get('asistencia_ultimo', 0)
    resolved_asist = tot_asist or asist_tot or asist_ult
    if not tot_asist and resolved_asist:
        result['total_asistencia'] = resolved_asist
    if not asist_tot and resolved_asist:
        result['asistencia_total'] = resolved_asist

    # Restringir ranking de redes al podio top 3 y sanitizar campos
    sanitized_ranking = []
    for r in result.get('ranking_redes', []):
        if isinstance(r, dict):
            try:
                cumpl = max(0, int(r.get('cumplimiento', 0) if r.get('cumplimiento') is not None else 0))
            except (ValueError, TypeError):
                cumpl = 0
            try:
                asist_sem = max(0, int(r.get('asistencia_semana', r.get('asistencia', 0)) if r.get('asistencia_semana', r.get('asistencia', 0)) is not None else 0))
            except (ValueError, TypeError):
                asist_sem = 0
            try:
                asist_tot_item = max(0, int(r.get('asistencia_total', 0) if r.get('asistencia_total') is not None else 0))
            except (ValueError, TypeError):
                asist_tot_item = 0
            try:
                casas_rep = max(0, int(r.get('casas_reportadas', 0) if r.get('casas_reportadas') is not None else 0))
            except (ValueError, TypeError):
                casas_rep = 0
            try:
                tot_c = max(0, int(r.get('total_casas', 0) if r.get('total_casas') is not None else 0))
            except (ValueError, TypeError):
                tot_c = 0

            color_cls = r.get('color_class') or 'default'
            if color_cls == 'default':
                n_clean = (r.get('nombre') or '').lower().strip()
                if 'sur' in n_clean:
                    color_cls = 'sur'
                elif 'central' in n_clean:
                    color_cls = 'central'
                elif 'hebr' in n_clean or 'cielo' in n_clean:
                    color_cls = 'hebron'

            sanitized_ranking.append({
                'nombre': str(r.get('nombre') or 'Sin nombre'),
                'supervisor': str(r.get('supervisor') or 'Sin supervisor'),
                'cumplimiento': cumpl,
                'asistencia': asist_sem,
                'asistencia_semana': asist_sem,
                'asistencia_total': asist_tot_item,
                'casas_reportadas': casas_rep,
                'total_casas': tot_c,
                'color_class': color_cls,
            })
    result['ranking_redes'] = sanitized_ranking[:3]
    
    # Asegurar dicts para crecimiento
    for key in ['top_crecimiento', 'bottom_crecimiento']:
        if key not in result or not isinstance(result.get(key), dict):
            result[key] = default_metricas[key]
    
    return result


def get_supervisor_red_id(usuario_id):
    """Obtiene el ID de la red asignada al supervisor."""
    if not usuario_id:
        return None
    conn = get_db_connection()
    if not conn:
        return 1  # Modo demo / offline cuando no hay base de datos conectada
    
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT r.id FROM red r WHERE r.supervisor_id = %s",
            (str(usuario_id),)
        )
        red_result = cur.fetchone()
        if red_result:
            return red_result['id']
        return None
    except Exception as e:
        print(f"[DB] Error obteniendo red del supervisor: {e}")
        return None
    finally:
        conn.close()


def get_selectores():
    """Obtiene las listas de redes y casas para los selectores del dashboard."""
    cache_key = f"selectores_db_{mock_mode_enabled()}"
    cached = get_cached_value(cache_key)
    
    if cached:
        return cached
    
    conn = get_db_connection()
    if not conn and mock_mode_enabled():
        return get_redes_demo(), get_casas_demo()
    if not conn:
        return [], []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.id, r.nombre, r.is_active, r.supervisor_id,
                   COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sin asignar') AS supervisor
            FROM red r
            LEFT JOIN usuario u ON r.supervisor_id = u.id
            ORDER BY r.nombre
        """)
        redes = cur.fetchall() or []
        
        cur.execute("""
            SELECT c.id, c.codigo, c.codigo AS nombre, c.anfitrion, c.direccion, c.red_id, c.is_active,
                   u.username AS usuario_username,
                   CONCAT(u.nombre, ' ', u.apellido) AS usuario_nombre,
                   COALESCE(
                       (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id AND l.rol = 'Lider' LIMIT 1),
                       (SELECT CONCAT(l.nombre, ' ', l.apellido) FROM lider l WHERE l.cdp_id = c.id LIMIT 1),
                       'Sin líder'
                   ) AS lider,
                   COALESCE(
                       (SELECT ROUND(AVG(nro_regulares + nro_niños + nro_visitas + nro_comprometidos)) 
                        FROM reporte WHERE cdp_id = c.id),
                       0
                   ) AS asistencia,
                   CASE 
                       WHEN c.is_active = 0 THEN 'pausada'
                       WHEN EXISTS(SELECT 1 FROM reporte WHERE cdp_id = c.id AND fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)) THEN 'activa'
                       ELSE 'pendiente'
                   END AS estado,
                   CASE
                       WHEN c.is_active = 1 AND EXISTS(SELECT 1 FROM reporte WHERE cdp_id = c.id AND fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)) THEN 1
                       ELSE 0
                   END AS tiene_reporte_7d,
                   (
                       SELECT r_last.hr_inicio
                       FROM reporte r_last
                       WHERE r_last.cdp_id = c.id AND r_last.hr_inicio IS NOT NULL
                       ORDER BY r_last.fecha DESC, r_last.id DESC
                       LIMIT 1
                   ) AS ultimo_hr_inicio,
                   (
                       SELECT r_last.fecha
                       FROM reporte r_last
                       WHERE r_last.cdp_id = c.id AND r_last.hr_inicio IS NOT NULL
                       ORDER BY r_last.fecha DESC, r_last.id DESC
                       LIMIT 1
                   ) AS ultima_fecha
            FROM cdp c
            LEFT JOIN usuario u ON c.usuario_id = u.id
            ORDER BY c.codigo
        """)
        casas = cur.fetchall() or []
        cur.close()
        
        result = (redes, casas)
        set_cached_value(cache_key, result)
        return result
    except Exception as e:
        print(f"[DB] Error obteniendo selectores: {e}")
        return [], []
    finally:
        conn.close()


def get_estructura_context(usuario_id, is_supervisor=False):
    """Obtiene redes y casas para la vista de estructura.

    Los datos demo solo se usan cuando MySQL no está disponible. Si la BD
    responde pero no tiene registros, la vista conserva estados vacíos.
    """
    conn = get_db_connection()
    db_connected = conn is not None
    if conn:
        conn.close()

    if db_connected:
        redes, casas = get_selectores()
    elif mock_mode_enabled():
        redes, casas = get_redes_demo(), get_casas_demo()
    else:
        redes, casas = [], []

    supervisor_red_id = None
    if is_supervisor:
        supervisor_red_id = get_supervisor_red_id(usuario_id) if db_connected else (redes[0]['id'] if redes else None)
        redes = [red for red in redes if red['id'] == supervisor_red_id]
        casas = [casa for casa in casas if casa['red_id'] == supervisor_red_id]

    def red_slug(red_id):
        return f'red-{red_id}'

    casas_por_red = {}
    for casa in casas:
        casas_por_red.setdefault(casa['red_id'], []).append(casa)

    redes_context = []
    for red in redes:
        redes_context.append({
            **red,
            'slug': red_slug(red['id']),
            'supervisor': red.get('supervisor') or 'Sin asignar',
            'total_casas': len(casas_por_red.get(red['id'], [])),
            'is_active': bool(red.get('is_active', 1)) if red.get('is_active') is not None else True,
        })

    casas_context = []
    for casa in casas:
        hr_raw = casa.get('ultimo_hr_inicio')
        fecha_raw = casa.get('ultima_fecha')
        if hr_raw or fecha_raw:
            horario_calc = formatear_horario_cdp(hr_raw, fecha_raw)
        else:
            horario_calc = casa.get('horario') or 'Miércoles · 7:00 PM'

        is_active = bool(casa.get('is_active', 1)) if casa.get('is_active') is not None else True
        if 'tiene_reporte_7d' in casa:
            tiene_rep = is_active and bool(casa.get('tiene_reporte_7d'))
        else:
            tiene_rep = is_active and (casa.get('estado') in ('activa', 'active'))

        if not is_active:
            estado = 'pausada'
            badge_class = 'status-pausada'
            badge_label = 'En pausa / Inactiva'
            pendiente_7d = False
            tiene_rep = False
        elif tiene_rep:
            estado = 'activa'
            badge_class = 'status-activa'
            badge_label = 'Reportó (últimos 7 días)'
            pendiente_7d = False
        else:
            estado = 'pendiente'
            badge_class = 'status-pendiente'
            badge_label = 'Sin reporte reciente'
            pendiente_7d = True

        casas_context.append({
            **casa,
            'red_slug': red_slug(casa['red_id']),
            'anfitrion': casa.get('anfitrion') or 'Sin anfitrión asignado',
            'lider': casa.get('lider') or 'Sin líder asignado',
            'usuario_username': casa.get('usuario_username'),
            'usuario_nombre': (casa.get('usuario_nombre') or '').strip(),
            'zona': casa.get('direccion') or 'Ubicación pendiente',
            'supervisor': casa.get('supervisor') or '',
            'is_active': is_active,
            'estado': estado,
            'tiene_reporte_7d': tiene_rep,
            'pendiente_7d': pendiente_7d,
            'badge_class': badge_class,
            'badge_label': badge_label,
            'horario': horario_calc,
            'asistencia': casa.get('asistencia') or 0,
        })

    total_asistencia = sum(c.get('asistencia', 0) for c in casas_context)
    casas_activas = sum(1 for c in casas_context if c.get('is_active'))
    casas_pausadas = sum(1 for c in casas_context if not c.get('is_active'))
    casas_pendientes_list = [c for c in casas_context if c.get('is_active') and not c.get('tiene_reporte_7d')]
    total_sin_reporte_7d = len(casas_pendientes_list)
    casas_sin_reporte_ids = [c['id'] for c in casas_pendientes_list]
    casas_sin_reporte_codigos = [c.get('codigo') or c.get('nombre') for c in casas_pendientes_list]

    return {
        'redes_estructura': redes_context,
        'casas_estructura': casas_context,
        'total_casas_estructura': len(casas_context),
        'total_asistencia_estructura': total_asistencia,
        'casas_activas_estructura': casas_activas,
        'casas_pausadas_estructura': casas_pausadas,
        'casas_pendientes_estructura': total_sin_reporte_7d,
        'total_sin_reporte_7d': total_sin_reporte_7d,
        'casas_sin_reporte_ids': casas_sin_reporte_ids,
        'casas_sin_reporte_codigos': casas_sin_reporte_codigos,
        'estructura_mock': not db_connected,
        'estructura_vacia': not redes_context,
    }


def get_casas_sin_reporte_7d(red_id=None):
    """
    Retorna la lista de Casas de Paz activas que no han reportado en los últimos 7 días.
    Si se pasa red_id, filtra por esa red.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT c.id, c.codigo, c.anfitrion, c.direccion, c.red_id, r.nombre AS red_nombre
                    FROM cdp c
                    LEFT JOIN red r ON c.red_id = r.id
                    WHERE c.is_active = 1
                      AND NOT EXISTS (
                          SELECT 1 FROM reporte rep
                          WHERE rep.cdp_id = c.id
                            AND rep.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                      )
                """
                params = []
                if red_id is not None:
                    sql += " AND c.red_id = %s"
                    params.append(red_id)
                sql += " ORDER BY c.codigo ASC"
                cur.execute(sql, tuple(params))
                return cur.fetchall() or []
        except Exception as e:
            print(f"[DB] Error al obtener casas sin reporte 7d: {e}")
            return []
        finally:
            conn.close()

    # Mock fallback
    casas = get_casas_demo()
    pendientes = [c for c in casas if c.get('is_active', 1) and not c.get('tiene_reporte_7d', True)]
    if red_id is not None:
        pendientes = [c for c in pendientes if c.get('red_id') == red_id]
    return pendientes


def get_metricas(nivel, red_id=None, cdp_id=None, is_supervisor=False, supervisor_red_id=None):
    """
    Obtiene las métricas según el nivel solicitado.
    
    Args:
        nivel: 'general', 'red', o 'cdp'
        red_id: ID de la red (opcional)
        cdp_id: ID de la casa de paz (opcional)
        is_supervisor: Si es supervisor, filtra por su red
        supervisor_red_id: ID de la red del supervisor
    
    Returns:
        dict con las métricas y flag mock_used
    """
    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}_{mock_mode_enabled()}'
    cached = get_cached_value(cache_key)
    
    if cached:
        return cached
    
    conn = get_db_connection()
    db_connected = conn is not None
    metricas = {}
    mock_used = False
    
    try:
        if nivel == 'general':
            if db_connected:
                metricas = get_metricas_generales(conn)
            elif mock_mode_enabled():
                metricas = get_mock_generales()
                mock_used = True
            else:
                metricas = get_empty_generales()
        
        elif nivel == 'red':
            rid = red_id or supervisor_red_id or 1
            if db_connected:
                result = get_metricas_red(conn, rid)
                metricas = result if result else get_empty_red(rid)
            elif mock_mode_enabled():
                metricas = get_mock_red(rid)
                mock_used = True
            else:
                metricas = get_empty_red(rid)
        
        elif nivel == 'cdp':
            if not cdp_id:
                metricas = get_empty_cdp(None)
            else:
                cid = cdp_id
                if db_connected:
                    result = get_metricas_cdp(conn, cid)
                    metricas = result if result else get_empty_cdp(cid)
                elif mock_mode_enabled():
                    metricas = get_mock_cdp(cid)
                    mock_used = True
                else:
                    metricas = get_empty_cdp(cid)
    except Exception as e:
        print(f"[Service] Error obteniendo métricas: {e}")
        metricas = get_empty_generales()
    finally:
        if conn:
            conn.close()
    
    # Sanitizar metricas para asegurar que todas las claves requeridas existan
    metricas = sanitize_metricas(metricas)
    
    result = {**metricas, 'mock_used': mock_used}
    set_cached_value(cache_key, result)
    return result


def get_dashboard_context(usuario_id, is_supervisor=False, default_nivel='general'):
    """
    Obtiene el contexto completo para el dashboard.
    
    Args:
        usuario_id: UUID del usuario (string)
        is_supervisor: Si es True, filtra datos solo a la red del supervisor
        default_nivel: Nivel por defecto ('general', 'red', 'cdp')
    
    Returns:
        dict con todas las variables necesarias para el template
    """
    nivel = request.args.get('nivel', default_nivel)
    red_id_str = request.args.get('red_id', '')
    cdp_id_str = request.args.get('cdp_id', '')

    # Parsear IDs
    try:
        red_id = int(red_id_str) if red_id_str and red_id_str.isdigit() else None
    except (ValueError, TypeError):
        red_id = None

    try:
        cdp_id = int(cdp_id_str) if cdp_id_str and cdp_id_str.isdigit() else None
    except (ValueError, TypeError):
        cdp_id = None

    usuario = session.get("usuario", "Administrador")
    db_connected = get_db_connection() is not None
    
    # Obtener red del supervisor si aplica
    supervisor_red_id = None
    sin_red_asignada = False
    if is_supervisor:
        supervisor_red_id = get_supervisor_red_id(usuario_id)
        if not supervisor_red_id:
            sin_red_asignada = True
            red_id = None
            cdp_id = None
        else:
            # Para supervisores con red, solo permitir niveles 'red' y 'cdp'
            if nivel not in ('red', 'cdp'):
                nivel = 'red'
            red_id = supervisor_red_id

    # Obtener selectores
    redes, casas = get_selectores()

    # Filtrar por red del supervisor si aplica
    if is_supervisor:
        if sin_red_asignada:
            redes = []
            casas = []
        else:
            redes = [r for r in redes if r['id'] == supervisor_red_id]
            casas = [c for c in casas if c['red_id'] == supervisor_red_id]

            # Seguridad: asegurar que el cdp_id pertenezca a la red del supervisor
            if nivel == 'cdp':
                casas_ids = [c['id'] for c in casas]
                if cdp_id and cdp_id not in casas_ids and casas_ids:
                    cdp_id = casas_ids[0]
                elif not cdp_id and casas_ids:
                    cdp_id = casas_ids[0]
    else:
        # Administrador: sincronización bidireccional y cascada server-side
        if nivel == 'cdp':
            # Si se dio un cdp_id y no un red_id, deducir la red del CDP
            if cdp_id and not red_id:
                cdp_match = next((c for c in casas if c['id'] == cdp_id), None)
                if cdp_match and cdp_match.get('red_id'):
                    red_id = cdp_match['red_id']
            # Si se especificó red_id, asegurar que el cdp_id pertenezca a esa red
            elif red_id:
                casas_de_red = [c for c in casas if c.get('red_id') == red_id]
                if casas_de_red:
                    if not cdp_id or cdp_id not in [c['id'] for c in casas_de_red]:
                        cdp_id = casas_de_red[0]['id']
                else:
                    cdp_id = None

    # Si se seleccionó nivel red o cdp sin ID específico, usar el primero disponible
    if not sin_red_asignada:
        if nivel == 'red' and not red_id and redes:
            red_id = redes[0]['id']
        elif nivel == 'cdp' and not cdp_id:
            # Solo hacer fallback si no hay red seleccionada (sin contexto previo)
            # Si red_id existe pero no tiene CDPs asignadas, respetar cdp_id = None
            if not red_id and casas:
                cdp_id = casas[0]['id']

    # Obtener métricas
    if sin_red_asignada:
        metricas = sanitize_metricas({})
        mock_used = False
    else:
        metricas = get_metricas(nivel, red_id, cdp_id, is_supervisor, supervisor_red_id)
        mock_used = metricas.pop('mock_used', False)

    # Si estamos en nivel cdp sin cdp asignada pero con red_id, asegurar nombre_red en métricas
    if nivel == 'cdp' and not cdp_id and red_id:
        red_obj = next((r for r in redes if r.get('id') == red_id), None)
        if red_obj and red_obj.get('nombre'):
            metricas['nombre_red'] = red_obj['nombre']

    return {
        'usuario': usuario,
        'nivel': nivel,
        'red_id': red_id,
        'cdp_id': cdp_id,
        'redes': redes,
        'casas': casas,
        'metricas': metricas,
        'db_connected': db_connected,
        'mock_used': mock_used,
        'sin_red_asignada': sin_red_asignada,
    }