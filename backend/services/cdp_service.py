"""
Servicio de Casa de Paz (CDP) - Lógica de negocio para Casas de Paz.
Las funciones de perfil y reportes viven en `services.profile_service` y
`services.report_service`, manteniéndose aquí como fachadas de compatibilidad hacia atrás.
"""
import logging
import uuid

from flask import current_app, request
from database import get_db_connection
from utils.cache import invalidate_dashboard_cache
import db_queries

from werkzeug.security import generate_password_hash, check_password_hash
from utils.validators import (
    validate_username,
    validate_password_strength,
    validate_person_name,
    validate_phone,
    format_whatsapp_digits,
)
from services import profile_service as _profile_service
from services import report_service as _report_service
from services.report_service import ProcessReporteResult, _parse_cesta_amor

logger = logging.getLogger(__name__)


def process_reporte(cdp_id, form_data):
    """Fachada retrocompatible hacia services.report_service.process_reporte."""
    return _report_service.process_reporte(
        cdp_id,
        form_data,
        _conn_provider=get_db_connection,
        _db_queries=db_queries,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def get_perfil_data(usuario_id):
    """Fachada retrocompatible hacia services.profile_service.get_perfil_data."""
    return _profile_service.get_perfil_data(usuario_id, _conn_provider=get_db_connection)


def update_perfil(usuario_id, nombre, apellido):
    """Fachada retrocompatible hacia services.profile_service.update_perfil."""
    return _profile_service.update_perfil(usuario_id, nombre, apellido, _conn_provider=get_db_connection)


def cambiar_username(usuario_id, nuevo_username):
    """Fachada retrocompatible hacia services.profile_service.cambiar_username."""
    return _profile_service.cambiar_username(usuario_id, nuevo_username, _conn_provider=get_db_connection)


def cambiar_password(usuario_id, password_actual, password_nueva):
    """Fachada retrocompatible hacia services.profile_service.cambiar_password."""
    return _profile_service.cambiar_password(
        usuario_id,
        password_actual,
        password_nueva,
        _conn_provider=get_db_connection,
    )

def get_cdp_datos_usuario(usuario_id):
    """
    Obtiene la Casa de Paz asignada y sus líderes asociados para el usuario en sesión.
    """
    conn = get_db_connection()
    if not conn:
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            from mock_data import get_casas_demo, get_mock_lideres
            casas = get_casas_demo()
            lideres_all = get_mock_lideres()
            cdp_match = next((c for c in casas if str(c.get('lider_id')) == str(usuario_id)), None)
            if not cdp_match:
                lider_match = next((l for l in lideres_all if str(l.get('usuario_id')) == str(usuario_id)), None)
                if lider_match:
                    cdp_match = next((c for c in casas if c['id'] == lider_match['cdp_id']), None)
            if not cdp_match:
                cdp_match = casas[0]

            lideres_cdp = [
                {'id': l['id'], 'nombre': l['nombre'], 'apellido': l['apellido'], 'rol': l['rol']}
                for l in lideres_all if l['cdp_id'] == cdp_match['id']
            ]
            return {
                'id': cdp_match['id'],
                'codigo': cdp_match['codigo'],
                'nombre': cdp_match['nombre'],
                'direccion': cdp_match['direccion'],
                'anfitrion': cdp_match['anfitrion']
            }, lideres_cdp
        return None, []
    
    try:
        with conn.cursor() as cursor:
            # 1. Obtener la CDP del usuario
            cdp = db_queries.obtener_cdp_por_usuario(cursor, usuario_id)
            if not cdp:
                return None, []

            # 2. Obtener los líderes de esa CDP
            lideres = db_queries.obtener_lideres_por_cdp(cursor, cdp['id'])
            
            return cdp, lideres
    except Exception as e:
        logger.error("[DB] Error al consultar datos de CDP y líderes: %s", e)
        return None, []
    finally:
        conn.close()


def get_lider_dashboard_data(usuario_id, page=1, per_page=5):
    """
    Recupera todo el contexto necesario para el dashboard del Líder de Casa de Paz:
    - Datos de la Casa de Paz asignada
    - Lista de líderes / sublíderes del equipo
    - Métricas consolidadas (reportes, asistencia promedio, ofrendas, etc.)
    - Historial de reportes registrados (paginado)
    """
    conn = get_db_connection()
    if not conn:
        # Fallback en caso de que no haya conexión (modo demo / mock)
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            from mock_data import get_mock_cdp, get_mock_lideres, get_mock_reportes, get_casas_demo
            casas = get_casas_demo()
            cdp_match = next((c for c in casas if str(c.get('lider_id')) == str(usuario_id)), None)
            cid = cdp_match['id'] if cdp_match else 1
            mock_cdp = get_mock_cdp(cid)

            lideres_list = [
                {'id': l['id'], 'nombre': l['nombre'], 'apellido': l['apellido'], 'rol': l['rol'], 'telefono': l['telefono']}
                for l in get_mock_lideres() if l['cdp_id'] == cid
            ]
            reps_cdp = [r for r in get_mock_reportes() if r['cdp_id'] == cid]
            total_reps = len(reps_cdp)
            start = (page - 1) * per_page
            mock_reps_page = reps_cdp[start:start + per_page]
            pages = max((total_reps + per_page - 1) // per_page, 1)

            return {
                'cdp': {'id': cid, 'codigo': mock_cdp['codigo'], 'anfitrion': mock_cdp['anfitrion']},
                'lideres': lideres_list,
                'metricas': {
                    'total_reportes': total_reps,
                    'asistencia_promedio': mock_cdp['promedio_historico'],
                    'ofrendas_usd_totales': sum(r['ofrendas_usd'] for r in reps_cdp),
                    'ofrendas_bs_totales': sum(r['ofrendas_bs'] for r in reps_cdp),
                    'visitas_totales': sum(r['nro_visitas'] for r in reps_cdp),
                    'conversiones_totales': sum(r['confesiones'] for r in reps_cdp),
                    'reconciliaciones_totales': sum(r['reconciliaciones'] for r in reps_cdp),
                    'reporte_esta_semana': True,
                    'dias_cierre_texto': 'Próximo cierre: 3 días',
                },
                'reportes': mock_reps_page,
                'total_reportes': total_reps,
                'page': page,
                'pages': pages,
                'tiene_cdp': True
            }

        return {
            'cdp': None,
            'lideres': [],
            'metricas': {
                'total_reportes': 0,
                'asistencia_promedio': 0,
                'ofrendas_usd_totales': 0.0,
                'ofrendas_bs_totales': 0.0,
                'visitas_totales': 0,
                'conversiones_totales': 0,
                'reconciliaciones_totales': 0,
                'reporte_esta_semana': False,
                'dias_cierre_texto': 'Próximo cierre: Domingo 6:00 PM',
            },
            'reportes': [],
            'total_reportes': 0,
            'page': 1,
            'pages': 1,
            'tiene_cdp': False
        }

    try:
        with conn.cursor() as cursor:
            # 1. Obtener la CDP del usuario
            cdp = db_queries.obtener_cdp_por_usuario(cursor, usuario_id)
            if not cdp:
                return {
                    'cdp': None,
                    'lideres': [],
                    'metricas': {
                        'total_reportes': 0,
                        'asistencia_promedio': 0,
                        'ofrendas_usd_totales': 0.0,
                        'ofrendas_bs_totales': 0.0,
                        'visitas_totales': 0,
                        'conversiones_totales': 0,
                        'reconciliaciones_totales': 0,
                        'reporte_esta_semana': False,
                        'dias_cierre_texto': 'Sin Casa de Paz asignada',
                    },
                    'reportes': [],
                    'total_reportes': 0,
                    'page': 1,
                    'pages': 1,
                    'tiene_cdp': False
                }

            cdp_id = cdp['id']

            # 2. Líderes de la CDP
            lideres = db_queries.obtener_lideres_por_cdp(cursor, cdp_id)

            # 3. Métricas consolidadas
            metricas = db_queries.obtener_metricas_lider_cdp(cursor, cdp_id)

            # 4. Lista de reportes con paginación
            todos_reportes = db_queries.obtener_reportes_por_cdp(cursor, cdp_id)
            total_reps = len(todos_reportes)
            start = (page - 1) * per_page
            reportes_page = todos_reportes[start:start + per_page]
            pages = max((total_reps + per_page - 1) // per_page, 1)

            return {
                'cdp': cdp,
                'lideres': lideres,
                'metricas': metricas,
                'reportes': reportes_page,
                'total_reportes': total_reps,
                'page': page,
                'pages': pages,
                'tiene_cdp': True
            }
    except Exception as e:
        logger.error("[DB] Error al cargar dashboard de líder CDP: %s", e)
        return {
            'cdp': None,
            'lideres': [],
            'metricas': {
                'total_reportes': 0,
                'asistencia_promedio': 0,
                'ofrendas_usd_totales': 0.0,
                'ofrendas_bs_totales': 0.0,
                'visitas_totales': 0,
                'conversiones_totales': 0,
                'reconciliaciones_totales': 0,
                'reporte_esta_semana': False,
                'dias_cierre_texto': 'Error al consultar datos',
            },
            'reportes': [],
            'total_reportes': 0,
            'page': 1,
            'pages': 1,
            'tiene_cdp': False
        }
    finally:
        conn.close()


def actualizar_reporte(reporte_id, cdp_id, form_data):
    """Fachada retrocompatible hacia services.report_service.actualizar_reporte."""
    return _report_service.actualizar_reporte(
        reporte_id,
        cdp_id,
        form_data,
        _conn_provider=get_db_connection,
        _db_queries=db_queries,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def eliminar_reporte(reporte_id, cdp_id):
    """Fachada retrocompatible hacia services.report_service.eliminar_reporte."""
    return _report_service.eliminar_reporte(
        reporte_id,
        cdp_id,
        _conn_provider=get_db_connection,
        _db_queries=db_queries,
        _invalidate_cache=invalidate_dashboard_cache,
    )


def get_cdp_detalle(cdp_id):
    """
    Obtiene todos los datos detallados de una Casa de Paz para la vista de detalles.
    Incluye métricas consolidadas, historial de reportes, líderes y enlaces de acción rápida.
    """
    import urllib.parse
    import re

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # 1. Datos básicos de la CDP y usuario del sistema asignado
                cur.execute("""
                    SELECT c.id, c.codigo, c.anfitrion, c.direccion, c.telefono, c.red_id, c.is_active, c.usuario_id,
                           r.nombre AS red_nombre,
                           u.username AS usuario_username,
                           u.nombre AS usuario_nombre,
                           u.apellido AS usuario_apellido,
                           u.is_active AS usuario_is_active,
                           COALESCE(CONCAT(u_sup.nombre, ' ', u_sup.apellido), 'Sin asignar') AS supervisor_nombre
                    FROM cdp c
                    LEFT JOIN red r ON c.red_id = r.id
                    LEFT JOIN usuario u ON c.usuario_id = u.id
                    LEFT JOIN usuario u_sup ON r.supervisor_id = u_sup.id
                    WHERE c.id = %s
                """, (cdp_id,))
                cdp = cur.fetchone()
                
                if cdp:
                    # 2. Líderes asignados a esta CDP
                    cur.execute("""
                        SELECT id, nombre, apellido, rol, telefono
                        FROM lider
                        WHERE cdp_id = %s
                        ORDER BY FIELD(rol, 'Lider', 'Sublider', 'Anfitrion'), nombre
                    """, (cdp_id,))
                    lideres = cur.fetchall() or []
                    
                    # 3. Métricas consolidadas
                    metricas = db_queries.obtener_metricas_lider_cdp(cur, cdp_id)
                    
                    # 4. Historial completo de reportes
                    reportes_historial = db_queries.obtener_reportes_por_cdp(cur, cdp_id)
                    
                    # Procesar miembros del equipo con iniciales y enlace de WhatsApp
                    team = []
                    for l in lideres:
                        nom = (l.get('nombre') or '').strip()
                        ape = (l.get('apellido') or '').strip()
                        ini = (nom[:1] + ape[:1]).upper() if (nom and ape) else (nom[:2].upper() if nom else 'LP')
                        tel = (l.get('telefono') or '').strip()
                        tel_wa = format_whatsapp_digits(tel) or None

                        team.append({
                            'id': l['id'],
                            'nombre_completo': f"{nom} {ape}".strip() or 'Líder',
                            'rol': l.get('rol', 'Líder'),
                            'telefono': tel,
                            'telefono_wa': tel_wa,
                            'iniciales': ini
                        })
                    
                    # Líder principal (de la tabla lider)
                    lider_principal = team[0]['nombre_completo'] if team else 'Sin líder asignado'
                    
                    # Teléfono propio de la Casa de Paz
                    tel_cdp = (cdp.get('telefono') or '').strip()
                    if tel_cdp and tel_cdp != 'No registrado':
                        telefono_contacto = tel_cdp
                        telefono_wa = format_whatsapp_digits(tel_cdp) or None
                    else:
                        telefono_contacto = 'No registrado'
                        telefono_wa = None
                    
                    # Dirección y query para Google Maps
                    direccion = cdp.get('direccion') or 'Sector Central'
                    maps_query = urllib.parse.quote_plus(f"{direccion}, Venezuela")

                    # Horario real derivado de los reportes (o base oficial: Miércoles · 7:00 PM)
                    hr_ini = reportes_historial[0].get('hr_inicio') if reportes_historial else None
                    fecha_val = reportes_historial[0].get('fecha') if reportes_historial else None
                    horario = db_queries.formatear_horario_cdp(hr_ini, fecha_val)

                    # Estado real de la Casa de Paz
                    is_active = bool(cdp.get('is_active', 1)) if cdp.get('is_active') is not None else True
                    estado = 'activa' if is_active else 'inactiva'

                    # Ventana móvil de los últimos 7 días para estado de reporte
                    from datetime import date, timedelta
                    hoy = date.today()
                    hace_7_dias = hoy - timedelta(days=7)
                    ultimo_rep = reportes_historial[0] if reportes_historial else None
                    ultimo_reporte_fecha = None
                    dias_desde_ultimo_reporte = None
                    tiene_reporte_reciente = False

                    if ultimo_rep and ultimo_rep.get('fecha'):
                        u_f = ultimo_rep['fecha']
                        if hasattr(u_f, 'date'):
                            u_f_date = u_f.date()
                        elif isinstance(u_f, date):
                            u_f_date = u_f
                        elif isinstance(u_f, str):
                            try:
                                u_f_date = date.fromisoformat(u_f[:10])
                            except Exception:
                                u_f_date = None
                        else:
                            u_f_date = None

                        if u_f_date:
                            dias_desde_ultimo_reporte = (hoy - u_f_date).days
                            if u_f_date >= hace_7_dias:
                                tiene_reporte_reciente = True

                        ultimo_reporte_fecha = ultimo_rep.get('fecha_formateada') or str(ultimo_rep.get('fecha') or '')

                    if not is_active:
                        estado_reporte_7d = 'pausada'
                        reporte_reciente_7d = False
                    elif tiene_reporte_reciente:
                        estado_reporte_7d = 'al_dia'
                        reporte_reciente_7d = True
                    else:
                        estado_reporte_7d = 'pendiente'
                        reporte_reciente_7d = False

                    return {
                        'id': cdp['id'],
                        'codigo': cdp['codigo'],
                        'red_id': cdp.get('red_id'),
                        'nombre': f"Casa \"{cdp['codigo']}\"",
                        'red_nombre': cdp.get('red_nombre') or 'Red Zonal',
                        'supervisor_nombre': cdp.get('supervisor_nombre') or 'Sin supervisor',
                        'direccion': direccion,
                        'maps_url': f"https://www.google.com/maps/search/?api=1&query={maps_query}",
                        'anfitrion': cdp.get('anfitrion') or 'Sin anfitrión asignado',
                        'lider_nombre': lider_principal,
                        'telefono': telefono_contacto,
                        'telefono_wa': telefono_wa,
                        'is_active': is_active,
                        'estado': estado,
                        'reporte_reciente_7d': reporte_reciente_7d,
                        'estado_reporte_7d': estado_reporte_7d,
                        'ultimo_reporte_fecha': ultimo_reporte_fecha,
                        'dias_desde_ultimo_reporte': dias_desde_ultimo_reporte,
                        'horario': horario,
                        'usuario_id': cdp.get('usuario_id'),
                        'usuario_username': cdp.get('usuario_username'),
                        'usuario_nombre': cdp.get('usuario_nombre') or '',
                        'usuario_apellido': cdp.get('usuario_apellido') or '',
                        'usuario_activo': bool(cdp.get('usuario_is_active', 1)) if cdp.get('usuario_is_active') is not None else True,
                        'asistencia_promedio': metricas.get('asistencia_promedio', 0),
                        'total_reportes': metricas.get('total_reportes', 0),
                        'ofrendas_usd_totales': metricas.get('ofrendas_usd_totales', 0.0),
                        'ofrendas_bs_totales': metricas.get('ofrendas_bs_totales', 0.0),
                        'visitas_totales': metricas.get('visitas_totales', 0),
                        'conversiones_totales': metricas.get('conversiones_totales', 0),
                        'reconciliaciones_totales': metricas.get('reconciliaciones_totales', 0),
                        'total_voluntarios': len(team),
                        'lideres': team,
                        'reportes': reportes_historial[:6]  # Mostrar los últimos 6
                    }
        except Exception as e:
            logger.error("[DB] Error al obtener detalles de CDP %s: %s", cdp_id, e)
            return None
        finally:
            conn.close()
        return None
            
    # Fallback demo estrictamente cuando MOCK_MODE está habilitado (nunca en producción ni con MOCK_MODE=False)
    from services.dashboard_service import mock_mode_enabled
    if mock_mode_enabled():
        from mock_data import get_mock_cdp_detalle
        return get_mock_cdp_detalle(cdp_id)

    return None

def get_lideres_cdp_disponibles_servicio(cdp_id=None):
    """
    Obtiene los usuarios con rol 'lider_cdp' disponibles para asignación a una Casa de Paz.
    Incluye al líder actualmente asignado si cdp_id es provisto (para edición).
    """
    conn = get_db_connection()
    if not conn:
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            from mock_data import get_mock_usuarios, get_casas_demo
            usuarios = get_mock_usuarios()
            casas = get_casas_demo()
            asignados_ids = {str(c.get('lider_id')) for c in casas if c.get('lider_id')}
            return [
                {
                    'id': u['id'],
                    'nombre': u['nombre'],
                    'apellido': u['apellido'],
                    'username': u['username']
                }
                for u in usuarios
                if u.get('rol') in ('lider_cdp', 'cdp') and (
                    str(u['id']) not in asignados_ids or (cdp_id and str(u.get('cdp_id')) == str(cdp_id))
                )
            ]
        return []

    try:
        with conn.cursor() as cursor:
            return db_queries.get_lideres_cdp_disponibles(cursor, cdp_id=cdp_id)
    except Exception as e:
        current_app.logger.error("Error al obtener líderes CDP disponibles: %s", e)
        return []
    finally:
        conn.close()

def _as_str(val, default: str = '') -> str:
    """Convierte de forma segura cualquier valor (str, int, None) a cadena sin espacios externos."""
    if val is None:
        return default
    return str(val).strip()


def crear_cdp_servicio(form_data: dict) -> tuple[bool, str]:
    """
    Crea la cuenta de usuario líder o asigna un usuario existente y registra la nueva Casa de Paz de forma transaccional.
    """
    codigo = _as_str(form_data.get('codigo'))
    anfitrion = _as_str(form_data.get('anfitrion'))
    telefono_raw = _as_str(form_data.get('telefono'))
    direccion = _as_str(form_data.get('direccion'))
    red_id_raw = _as_str(form_data.get('red_id'))

    modo_usuario = _as_str(form_data.get('modo_usuario'), 'nuevo')
    usuario_existente_id = _as_str(
        form_data.get('usuario_existente_id')
        or form_data.get('usuario_id')
        or form_data.get('lider_id')
    )

    # Credenciales y datos del usuario (si es nuevo)
    nombre_user = _as_str(form_data.get('nombre') or form_data.get('nuevo_usuario_nombre'))
    apellido_user = _as_str(form_data.get('apellido') or form_data.get('nuevo_usuario_apellido'))
    username_raw = _as_str(form_data.get('username') or form_data.get('nuevo_usuario_username'))
    password_raw = _as_str(form_data.get('password') or form_data.get('nuevo_usuario_password'))

    # 1. Validaciones de datos de la Casa
    if not codigo or len(codigo) < 2:
        return False, "El código de la Casa de Paz debe tener al menos 2 caracteres."
    if not direccion or len(direccion) < 5:
        return False, "Debe indicar una dirección física válida."

    ok_anf, res_anfitrion = validate_person_name(anfitrion, "Anfitrión")
    if not ok_anf:
        return False, res_anfitrion

    ok_tel, res_tel, err_tel = validate_phone(telefono_raw)
    if not ok_tel:
        return False, err_tel

    try:
        red_id = int(red_id_raw)
    except (ValueError, TypeError):
        return False, "Debe seleccionar una Red Ministerial válida."

    # Determinar si se asigna un usuario existente
    es_modo_existente = (modo_usuario == 'existente') or (bool(usuario_existente_id) and not username_raw)

    if es_modo_existente:
        if not usuario_existente_id:
            return False, "Debe seleccionar un usuario líder para la Casa de Paz."
    else:
        # 2. Validaciones de credenciales de usuario nuevo
        ok_user, res_user = validate_username(username_raw)
        if not ok_user:
            return False, res_user

        ok_pass, err_pass = validate_password_strength(password_raw)
        if not ok_pass:
            return False, err_pass

        ok_nom, res_nom = validate_person_name(nombre_user, 'Nombre del Responsable')
        if not ok_nom:
            return False, res_nom
        
        ok_apellido, res_apellido = validate_person_name(apellido_user, 'Apellido del Responsable')
        if not ok_apellido:
            return False, res_apellido  
    
    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # 3. Validar código único de CDP
            cursor.execute("SELECT id FROM cdp WHERE codigo = %s", (codigo,))
            if cursor.fetchone():
                return False, f"Ya existe una Casa de Paz con el código '{codigo}'."

            if es_modo_existente:
                # 4. Validar existencia y disponibilidad del usuario existente
                cursor.execute("""
                    SELECT id, username, tipo_usuario, is_active 
                    FROM usuario 
                    WHERE id = %s
                """, (usuario_existente_id,))
                user_row = cursor.fetchone()
                if not user_row:
                    return False, "El usuario seleccionado no existe."
                if user_row.get('tipo_usuario') != 'lider_cdp':
                    return False, "El usuario seleccionado no tiene el rol de líder de Casa de Paz."
                if not user_row.get('is_active', 1):
                    return False, "El usuario seleccionado se encuentra inactivo."

                cursor.execute("SELECT id, codigo FROM cdp WHERE usuario_id = %s", (usuario_existente_id,))
                cdp_ocupada = cursor.fetchone()
                if cdp_ocupada:
                    return False, f"El usuario '@{user_row.get('username')}' ya está asignado a la Casa de Paz '{cdp_ocupada.get('codigo')}'."

                id_usuario_final = usuario_existente_id
                username_final = user_row.get('username', '')
            else:
                # 4. Validar username único
                cursor.execute("SELECT id FROM usuario WHERE username = %s", (res_user,))
                if cursor.fetchone():
                    return False, f"El nombre de usuario '{res_user}' ya está en uso."

                # 5. Insertar primero el Usuario nuevo
                nuevo_user_id = str(uuid.uuid4())
                pass_hash = generate_password_hash(password_raw)

                cursor.execute("""
                    INSERT INTO usuario (id, username, password, tipo_usuario, is_active, nombre, apellido)
                    VALUES (%s, %s, %s, 'lider_cdp', 1, %s, %s)
                """, (nuevo_user_id, res_user, pass_hash, res_nom, res_apellido))

                id_usuario_final = nuevo_user_id
                username_final = res_user

            # 6. Insertar Casa de Paz vinculada al usuario
            db_queries.insertar_cdp(cursor, codigo, res_anfitrion, direccion, res_tel, red_id, id_usuario_final)

            conn.commit()
            try:
                invalidate_dashboard_cache()
            except Exception:
                pass

            if es_modo_existente:
                return True, f"Casa de Paz '{codigo}' creada y asignada exitosamente al líder '@{username_final}'."
            else:
                return True, f"Casa de Paz '{codigo}' y usuario '@{username_final}' creados exitosamente."
        
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al crear CDP: %s", e)
        return False, "Error interno al registrar la Casa de Paz."
    finally:
        conn.close()

def actualizar_cdp_servicio(cdp_id: int, form_data: dict, is_active: int = None) -> tuple[bool, str]: 
    """Actualiza los datos de la Casa de Paz y del usuario líder vinculado."""

    try:
        cdp_id = int(cdp_id)
    except (ValueError, TypeError):
        return False, "Identificador de Casa de Paz no válido."

    codigo = _as_str(form_data.get('codigo'))
    anfitrion = _as_str(form_data.get('anfitrion'))
    telefono_raw = _as_str(form_data.get('telefono'))
    direccion = _as_str(form_data.get('direccion'))
    red_id_raw = _as_str(form_data.get('red_id'))

    modo_usuario = _as_str(form_data.get('modo_usuario'))
    usuario_existente_id = _as_str(
        form_data.get('usuario_existente_id')
        or form_data.get('usuario_id')
        or form_data.get('lider_id')
    )

    nombre_user = _as_str(form_data.get('nombre') or form_data.get('nuevo_usuario_nombre'))
    apellido_user = _as_str(form_data.get('apellido') or form_data.get('nuevo_usuario_apellido'))
    username_raw = _as_str(form_data.get('username') or form_data.get('nuevo_usuario_username'))
    password_nueva = _as_str(form_data.get('password') or form_data.get('nuevo_usuario_password'))

    is_active_raw = is_active if is_active is not None else form_data.get('is_active')
    is_active_val = None
    if is_active_raw is not None and str(is_active_raw).strip() != '':
        is_active_val = 1 if str(is_active_raw).strip().lower() in ('1', 'true', 'on', 'si', 'sí') or is_active_raw is True or is_active_raw == 1 else 0

    # 1. Validaciones de datos de la Casa
    if not codigo or len(codigo) < 2:
        return False, "El código de la Casa de Paz debe tener al menos 2 caracteres."
    if not direccion or len(direccion) < 5:
        return False, "Debe indicar una dirección física válida."

    ok_anf, res_anf = validate_person_name(anfitrion, "Anfitrión")
    if not ok_anf:
        return False, res_anf

    ok_tel, res_tel, err_tel = validate_phone(telefono_raw)
    if not ok_tel:
        return False, err_tel

    try:
        red_id = int(red_id_raw)
    except (ValueError, TypeError):
        return False, "Debe seleccionar una Red Ministerial válida."

    has_user_fields = bool(username_raw or nombre_user or apellido_user)
    es_modo_existente = bool(usuario_existente_id) and not username_raw

    res_nom = res_ape = res_user = ''
    if not es_modo_existente and has_user_fields:
        # 2. Validaciones de credenciales de usuario
        ok_nom, res_nom = validate_person_name(nombre_user, 'Nombre del Responsable')
        if not ok_nom:
            return False, res_nom

        ok_ape, res_ape = validate_person_name(apellido_user, 'Apellido del Responsable')
        if not ok_ape:
            return False, res_ape

        ok_user, res_user = validate_username(username_raw)
        if not ok_user:
            return False, res_user

        if password_nueva:
            ok_pass, err_pass = validate_password_strength(password_nueva)
            if not ok_pass:
                return False, err_pass
    elif modo_usuario == 'existente' and not usuario_existente_id and not form_data.get('_allow_keep_user', True):
        return False, "Debe seleccionar un usuario líder para la Casa de Paz."

    conn = get_db_connection()
    if not conn:
        return False, "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            # Comprobar que existe la Casa de Paz
            cursor.execute("SELECT id, usuario_id FROM cdp WHERE id = %s", (cdp_id,))
            fila_cdp = cursor.fetchone()
            if not fila_cdp:
                return False, "La Casa de Paz no existe."

            user_id = fila_cdp.get('usuario_id')

            # Validar jerarquía de Red si se solicita activar
            if is_active_val == 1:
                cursor.execute("SELECT id, nombre, is_active FROM red WHERE id = %s", (red_id,))
                red_parent = cursor.fetchone()
                if not red_parent:
                    return False, "La Red Ministerial seleccionada no existe."
                if not red_parent.get('is_active', 1):
                    return False, f"No se puede reactivar la Casa de Paz '{codigo}' porque su Red Ministerial '{red_parent.get('nombre', '')}' se encuentra en pausa. Debe reactivar la Red primero."

            # Comprobar duplicado de código en otra CDP
            cursor.execute("SELECT id FROM cdp WHERE codigo = %s AND id != %s", (codigo, cdp_id))
            if cursor.fetchone():
                return False, f"Ya existe otra Casa de Paz con el código '{codigo}'."

            # Actualizar datos de la Casa
            if is_active_val is not None:
                db_queries.actualizar_cdp_admin(cursor, cdp_id, codigo, res_anf, res_tel, direccion, red_id, is_active=is_active_val)
            else:
                db_queries.actualizar_cdp_admin(cursor, cdp_id, codigo, res_anf, res_tel, direccion, red_id)

            if es_modo_existente:
                # Comprobar que el usuario existente sea válido
                cursor.execute("SELECT id, username, tipo_usuario, is_active FROM usuario WHERE id = %s", (usuario_existente_id,))
                user_existente = cursor.fetchone()
                if not user_existente:
                    return False, "El usuario seleccionado no existe."
                if user_existente.get('tipo_usuario') != 'lider_cdp':
                    return False, "El usuario seleccionado no tiene el rol de líder de Casa de Paz."
                if not user_existente.get('is_active', 1):
                    return False, "El usuario seleccionado se encuentra inactivo."

                # Comprobar que no esté asignado a otra CDP distinta a la actual
                cursor.execute("SELECT id, codigo FROM cdp WHERE usuario_id = %s AND id != %s", (usuario_existente_id, cdp_id))
                cdp_otra = cursor.fetchone()
                if cdp_otra:
                    return False, f"El usuario '@{user_existente.get('username')}' ya está asignado a otra Casa de Paz ('{cdp_otra.get('codigo')}')."

                cursor.execute("UPDATE cdp SET usuario_id = %s WHERE id = %s", (usuario_existente_id, cdp_id))
            elif has_user_fields:
                # Comprobar unicidad de username excluyendo al usuario actual si existe
                if user_id:
                    cursor.execute("SELECT id FROM usuario WHERE username = %s AND id != %s", (res_user, str(user_id)))
                else:
                    cursor.execute("SELECT id FROM usuario WHERE username = %s", (res_user,))
                if cursor.fetchone():
                    return False, f"El nombre de usuario '{res_user}' ya está en uso."

                # Actualizar o crear usuario de acceso
                if user_id:
                    if password_nueva:
                        pass_hash = generate_password_hash(password_nueva)
                        cursor.execute("""
                            UPDATE usuario
                            SET nombre = %s, apellido = %s, username = %s, password = %s
                            WHERE id = %s
                        """, (res_nom, res_ape, res_user, pass_hash, str(user_id)))
                    else:
                        cursor.execute("""
                            UPDATE usuario
                            SET nombre = %s, apellido = %s, username = %s
                            WHERE id = %s
                        """, (res_nom, res_ape, res_user, str(user_id)))
                else:
                    if not password_nueva:
                        return False, "Debe ingresar una contraseña para crear las credenciales de acceso."
                    pass_hash = generate_password_hash(password_nueva)
                    nuevo_user_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO usuario (id, username, password, tipo_usuario, is_active, nombre, apellido)
                        VALUES (%s, %s, %s, 'lider_cdp', 1, %s, %s)
                    """, (nuevo_user_id, res_user, pass_hash, res_nom, res_ape))
                    cursor.execute("UPDATE cdp SET usuario_id = %s WHERE id = %s", (nuevo_user_id, cdp_id))

            # Sincronizar estado del usuario vinculado si se especificó is_active
            if is_active_val is not None:
                if es_modo_existente:
                    target_sync_uid = usuario_existente_id
                elif not user_id:
                    target_sync_uid = locals().get('nuevo_user_id')
                else:
                    target_sync_uid = str(user_id)
                if target_sync_uid:
                    cursor.execute("UPDATE usuario SET is_active = %s WHERE id = %s", (is_active_val, str(target_sync_uid)))

        conn.commit()

        try:
            invalidate_dashboard_cache()
        except Exception:
            pass

        return True, "Casa de Paz actualizada exitosamente."
    
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al actualizar CDP %s: %s", cdp_id, e)
        return False, "Error interno al actualizar la Casa de Paz."
    finally:
        conn.close()


def toggle_cdp_servicio(cdp_id: int) -> tuple[bool, str, str]:
    """
    Alterna el estado (pausa o reactivación) de una Casa de Paz y su cuenta vinculada.
    Valida la jerarquía con la Red Ministerial correspondiente.
    Retorna: (ok: bool, status: str, message: str)
    status: 'reactivada' | 'pausada' | 'bloqueada' | 'error'
    """
    try:
        cdp_id = int(cdp_id)
    except (ValueError, TypeError):
        return False, 'error', "Identificador de Casa de Paz no válido."

    conn = get_db_connection()
    if not conn:
        return False, 'error', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:
            ok, status, mensaje = db_queries.toggle_estado_cdp(cursor, cdp_id)
            if ok:
                conn.commit()
                try:
                    invalidate_dashboard_cache()
                except Exception:
                    pass
                return True, status, mensaje
            else:
                conn.rollback()
                return False, status, mensaje
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al alternar estado de CDP %s: %s", cdp_id, e)
        return False, 'error', "Error interno al alternar el estado de la Casa de Paz."
    finally:
        conn.close()

def eliminar_cdp_servicio(cdp_id: int) -> tuple[bool, str, str]:
    """Gestiona la baja o soft delete de una CDP llamando a eliminar_pausar_cdp."""

    try:
        cdp_id = int(cdp_id)
    except (ValueError, TypeError):
        return False, 'danger', "Identificador de Casa de Paz no válido."

    conn = get_db_connection()
    if not conn:
        return False, 'danger', "Error de conexión a la base de datos."

    try:
        with conn.cursor() as cursor:

            exito, accion, mensaje = db_queries.eliminar_pausar_cdp(cursor, cdp_id)

            # Asignamos la categoría visual de Bootstrap/CSS según la acción:
            categorias = {
                'eliminada': 'success',  # Verde
                'pausada':   'warning',  # Amarillo/Ámbar (aviso de que se pausó)
                'bloqueada': 'danger',   # Rojo (bloqueo por líderes asociados)
                'error':     'danger'    # Rojo
            }

            categoria_flash = categorias.get(accion, 'info')

            if exito:
                conn.commit()
                try:
                    invalidate_dashboard_cache()
                except Exception:
                    pass
                return True, categoria_flash, mensaje
            else:
                conn.rollback()
                return False, categoria_flash, mensaje
            
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error en baja de CDP %s: %s", cdp_id, e)
        return False, 'danger', "Error interno al procesar la baja de la Casa de Paz."
    finally:
        conn.close()


def check_cdp_reporte_7d(cdp_id) -> dict:
    """
    Verifica si una Casa de Paz activa ha enviado al menos un reporte en los últimos 7 días.
    Si is_active = 0, la casa está en pausa/inactiva y no cuenta como pendiente.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, codigo, is_active FROM cdp WHERE id = %s", (cdp_id,))
                cdp = cur.fetchone()
                if not cdp:
                    return {'cdp_id': cdp_id, 'tiene_reporte': False, 'is_active': False, 'estado': 'inactiva'}
                
                is_active = bool(cdp.get('is_active', 1))
                if not is_active:
                    return {'cdp_id': cdp_id, 'codigo': cdp.get('codigo'), 'tiene_reporte': False, 'is_active': False, 'estado': 'pausada'}

                from datetime import date, timedelta
                hace_7d = date.today() - timedelta(days=7)
                cur.execute("""
                    SELECT id, fecha FROM reporte 
                    WHERE cdp_id = %s AND fecha >= %s
                    ORDER BY fecha DESC LIMIT 1
                """, (cdp_id, hace_7d))
                rep = cur.fetchone()
                tiene_rep = rep is not None
                estado = 'al_dia' if tiene_rep else 'pendiente'
                return {
                    'cdp_id': cdp_id,
                    'codigo': cdp.get('codigo'),
                    'tiene_reporte': tiene_rep,
                    'is_active': True,
                    'estado': estado
                }
        except Exception as e:
            logger.error("[DB] Error checking cdp 7d: %s", e)
        finally:
            conn.close()

    # Demo fallback
    from services.dashboard_service import mock_mode_enabled
    if mock_mode_enabled():
        detalle = get_cdp_detalle(cdp_id)
        if detalle:
            return {
                'cdp_id': detalle.get('id', cdp_id),
                'codigo': detalle.get('codigo', ''),
                'tiene_reporte': bool(detalle.get('reporte_reciente_7d', False)),
                'is_active': bool(detalle.get('is_active', True)),
                'estado': detalle.get('estado_reporte_7d', 'pendiente')
            }

    return {'cdp_id': cdp_id, 'tiene_reporte': False, 'is_active': False, 'estado': 'inactiva'}


def get_casas_sin_reporte_7d(red_id=None):
    """
    Retorna la lista de Casas de Paz activas que no han reportado en los últimos 7 días.
    """
    from services.dashboard_service import get_casas_sin_reporte_7d as _get_sin_rep
    return _get_sin_rep(red_id=red_id)

def obtener_cdps_para_select():
    """Retorna las Casas de Paz activas para desplegables en formularios."""
    conn = get_db_connection()
    if not conn:
        from services.dashboard_service import mock_mode_enabled
        if mock_mode_enabled():
            from mock_data import get_casas_demo
            return [c for c in get_casas_demo() if c.get('is_active', 1) == 1]
        return []

    try:
        with conn.cursor() as cursor:
            return db_queries.get_cdps_para_lideres(cursor)
    except Exception as e:
        conn.rollback()
        current_app.logger.error("Error al obtener CDPs para select: %s", e)
        return []
    finally:
        conn.close()