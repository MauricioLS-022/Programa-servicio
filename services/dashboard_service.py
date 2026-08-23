"""
Servicio de dashboard - Lógica de negocio para métricas del dashboard.
Maneja la obtención y filtrado de métricas para Admin y Supervisor.
"""
from flask import session, request
from database import get_db_connection
from db_queries import get_metricas_generales, get_metricas_red, get_metricas_cdp
from mock_data import (
    get_redes_demo, get_casas_demo,
    get_mock_generales, get_mock_red, get_mock_cdp,
    get_empty_generales, get_empty_red, get_empty_cdp,
)
from utils.cache import get_cached_value, set_cached_value


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
    cache_key = 'selectores'
    cached = get_cached_value(cache_key)
    
    if cached:
        return cached
    
    conn = get_db_connection()
    if not conn:
        return get_redes_demo(), get_casas_demo()
    
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
            SELECT c.id, c.codigo, c.codigo AS nombre, c.red_id,
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
        return get_redes_demo(), get_casas_demo()
    finally:
        conn.close()


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
    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}'
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
            else:
                metricas = get_mock_generales()
                mock_used = True
        
        elif nivel == 'red':
            rid = red_id or supervisor_red_id or 1
            if db_connected:
                result = get_metricas_red(conn, rid)
                metricas = result if result else get_empty_red(rid)
            else:
                metricas = get_mock_red(rid)
                mock_used = True
        
        elif nivel == 'cdp':
            cid = cdp_id or 1
            if db_connected:
                result = get_metricas_cdp(conn, cid)
                metricas = result if result else get_empty_cdp(cid)
            else:
                metricas = get_mock_cdp(cid)
                mock_used = True
    except Exception as e:
        print(f"[Service] Error obteniendo métricas: {e}")
        metricas = get_empty_generales()
    finally:
        if conn:
            conn.close()
    
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