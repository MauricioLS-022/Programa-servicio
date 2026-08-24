"""
Servicio de dashboard - Lógica de negocio para métricas del dashboard.
Maneja la obtención y filtrado de métricas para Admin y Supervisor.
"""
from flask import current_app, session, request
from database import get_db_connection
from db_queries import get_metricas_generales, get_metricas_red, get_metricas_cdp
from mock_data import (
    get_redes_demo, get_casas_demo,
    get_mock_generales, get_mock_red, get_mock_cdp,
    get_empty_generales, get_empty_red, get_empty_cdp,
)
from utils.cache import get_cached_value, set_cached_value


def mock_mode_enabled():
    """Indica si los datos demo están explícitamente habilitados en desarrollo."""
    return (
        current_app.config.get('FLASK_ENV') == 'development'
        and current_app.config.get('MOCK_MODE', False)
    )


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
        'ofrendas': 0,
    }
    
    # Merge con valores por defecto
    result = {**default_metricas, **metricas}
    
    # Asegurar sub-diccionarios
    if 'distribucion' not in result or not isinstance(result.get('distribucion'), dict):
        result['distribucion'] = default_metricas['distribucion']
    
    # Asegurar listas
    for key in ['historial', 'tendencia', 'ranking_redes', 'ranking_cdp']:
        if key not in result or not isinstance(result.get(key), list):
            result[key] = []
    
    # Asegurar dicts para crecimiento
    for key in ['top_crecimiento', 'bottom_crecimiento']:
        if key not in result or not isinstance(result.get(key), dict):
            result[key] = default_metricas[key]
    
    return result


def get_supervisor_red_id(usuario_id):
    """Obtiene el ID de la red asignada al supervisor."""
    conn = get_db_connection()
    if not conn:
        return 1  # Default para modo demo
    
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT r.id FROM red r WHERE r.supervisor_id = %s",
            (str(usuario_id),)
        )
        red_result = cur.fetchone()
        if red_result:
            return red_result['id']
        return 1
    except Exception as e:
        print(f"[DB] Error obteniendo red del supervisor: {e}")
        return 1
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
            SELECT r.id, r.nombre,
                   CONCAT(u.nombre, ' ', u.apellido) AS supervisor
            FROM red r
            LEFT JOIN usuario u ON r.supervisor_id = u.id
            ORDER BY r.nombre
        """)
        redes = cur.fetchall()
        
        cur.execute("""
            SELECT c.id, c.codigo, c.codigo AS nombre, c.anfitrion, c.direccion, c.red_id,
                   CONCAT(l.nombre, ' ', l.apellido) AS lider
            FROM cdp c
            LEFT JOIN lider l ON l.cdp_id = c.id AND l.rol = 'Lider'
            ORDER BY c.codigo
        """)
        casas = cur.fetchall()
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
        })

    casas_context = []
    for casa in casas:
        casas_context.append({
            **casa,
            'red_slug': red_slug(casa['red_id']),
            'anfitrion': casa.get('anfitrion') or 'Sin anfitrión asignado',
            'zona': casa.get('direccion') or 'Ubicación pendiente',
            'supervisor': casa.get('supervisor') or '',
            'estado': casa.get('estado') or 'pendiente',
            'horario': casa.get('horario') or 'Horario pendiente',
            'asistencia': casa.get('asistencia') or 0,
        })

    return {
        'redes_estructura': redes_context,
        'casas_estructura': casas_context,
        'total_casas_estructura': len(casas_context),
        'estructura_mock': not db_connected,
        'estructura_vacia': not redes_context,
    }


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
            cid = cdp_id or 1
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
    if is_supervisor:
        supervisor_red_id = get_supervisor_red_id(usuario_id)
        # Forzar nivel a 'red' para supervisores
        if nivel == 'general':
            nivel = 'red'
        red_id = supervisor_red_id

    # Obtener selectores
    redes, casas = get_selectores()

    # Filtrar por red del supervisor si aplica
    if is_supervisor:
        redes = [r for r in redes if r['id'] == supervisor_red_id] if supervisor_red_id else redes[:1]
        casas = [c for c in casas if c['red_id'] == supervisor_red_id] if supervisor_red_id else casas

    # Obtener métricas
    metricas = get_metricas(nivel, red_id, cdp_id, is_supervisor, supervisor_red_id)
    mock_used = metricas.pop('mock_used', False)

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
    }