"""
Servicio de Casa de Paz (CDP) - Lógica de negocio para reportes y perfiles.
"""
from flask import request
from database import get_db_connection
from utils.cache import invalidate_dashboard_cache
import db_queries

def _parse_cesta_amor(val):
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return 1 if val > 0 else 0
    val_str = str(val).strip().lower()
    return 1 if val_str in ('1', 'true', 'si', 'sí', 'on') else 0


def process_reporte(cdp_id, form_data):
    """
    Valida y procesa el guardado de un reporte de Casa de Paz.
    """
    # 1. Preparación y conversión de datos (incluye los campos de reportes)
    ofrendas_usd = float(form_data.get('ofrendas_usd', form_data.get('ofrendas', 0.0)) or 0.0)
    ofrendas_bs = float(form_data.get('ofrendas_bs', 0.0) or 0.0)
    datos_reporte = {
        'cdp_id': cdp_id,
        'lider_id': form_data.get('lider_id') or None,
        'fecha': form_data.get('fecha'),
        'hr_inicio': form_data.get('hr_inicio'),
        'hr_fin': form_data.get('hr_fin'),
        'tema': form_data.get('tema', '').strip(),
        'nro_ninos': int(form_data.get('nro_ninos', 0) or 0),
        'nro_regulares': int(form_data.get('nro_regulares', 0) or 0),
        'nro_visitas': int(form_data.get('nro_visitas', 0) or 0),
        'nro_comprometidos': int(form_data.get('nro_comprometidos', 0) or 0),
        'reconciliaciones': int(form_data.get('reconciliaciones', 0) or 0),
        'confesiones': int(form_data.get('confesiones', 0) or 0),
        'ofrendas': ofrendas_usd,
        'ofrendas_usd': ofrendas_usd,
        'ofrendas_bs': ofrendas_bs,
        'cesta_amor': _parse_cesta_amor(form_data.get('cesta_amor', 0)),
        'observaciones': form_data.get('observaciones', '').strip()
    }
    # 2. Control de conexión a base de datos
    conn = get_db_connection()
    if not conn:
        print("[ERROR] No se pudo establecer conexión a la base de datos.")
        return False

    try:
        with conn.cursor() as cursor:
            db_queries.insertar_reporte(cursor, datos_reporte)
        conn.commit()  # Confirmar la transacción
        
        # Invalida cache del dashboard
        try:
            invalidate_dashboard_cache()
        except Exception as cache_err:
            print(f"[WARN] No se pudo invalidar la caché: {cache_err}")

        return True
    except Exception as e:
        conn.rollback()  # Revertir en caso de error
        print(f"[ERROR] Error al guardar reporte: {e}")
        return False
    finally:
        conn.close()



def get_perfil_data(usuario_id):
    """
    Obtiene los datos del perfil del usuario.
    
    Returns:
        dict con los datos del perfil
    """
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, nombre, apellido, email, tipo_usuario
                FROM usuario 
                WHERE id = %s
            """, (str(usuario_id),))
            return cursor.fetchone() or {}
    except Exception as e:
        print(f"[DB] Error perfil: {e}")
        return {}
    finally:
        conn.close()


def update_perfil(usuario_id, nombre, apellido):
    """
    Actualiza los datos del perfil del usuario (nombre y apellido).
    
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario 
                SET nombre = %s, apellido = %s
                WHERE id = %s
            """, (nombre, apellido, str(usuario_id)))
        conn.commit()
        return True, "Perfil actualizado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"[DB] Error actualizando perfil: {e}")
        return False, f"Error al actualizar perfil: {e}"
    finally:
        conn.close()


def cambiar_username(usuario_id, nuevo_username):
    """
    Cambia el nombre de usuario verificando que no exista duplicado.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not nuevo_username or len(nuevo_username.strip()) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"
    
    nuevo_username = nuevo_username.strip()
    
    if len(nuevo_username) > 30:
        return False, "El nombre de usuario no puede exceder 30 caracteres"
    
    conn = get_db_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    
    try:
        with conn.cursor() as cursor:
            # Verificar que el nuevo username no esté en uso por otro usuario
            cursor.execute("""
                SELECT id FROM usuario WHERE username = %s AND id != %s
            """, (nuevo_username, str(usuario_id)))
            
            if cursor.fetchone():
                return False, "Ese nombre de usuario ya está en uso"
            
            cursor.execute("""
                UPDATE usuario SET username = %s WHERE id = %s
            """, (nuevo_username, str(usuario_id)))
        
        conn.commit()
        return True, "Nombre de usuario actualizado exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"[DB] Error cambiando username: {e}")
        return False, f"Error al cambiar el nombre de usuario: {e}"
    finally:
        conn.close()


def cambiar_password(usuario_id, password_actual, password_nueva):
    """
    Cambia la contraseña verificando la contraseña actual.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from werkzeug.security import generate_password_hash, check_password_hash
    
    if not password_nueva or len(password_nueva) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres"
    
    conn = get_db_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos"
    
    try:
        with conn.cursor() as cursor:
            # Obtener hash almacenado
            cursor.execute("""
                SELECT password FROM usuario WHERE id = %s
            """, (str(usuario_id),))
            row = cursor.fetchone()
            
            if not row:
                return False, "Usuario no encontrado"
            
            stored_hash = row.get('password', '')
            
            # Verificar contraseña actual (soporta hash Werkzeug y legacy plaintext)
            password_valida = False
            if stored_hash.count('$') < 2:
                # Contraseña legacy (plaintext)
                password_valida = (stored_hash == password_actual)
            else:
                try:
                    password_valida = check_password_hash(stored_hash, password_actual)
                except (ValueError, TypeError):
                    password_valida = False
            
            if not password_valida:
                return False, "La contraseña actual es incorrecta"
            
            # Generar nuevo hash y actualizar
            nuevo_hash = generate_password_hash(password_nueva)
            cursor.execute("""
                UPDATE usuario SET password = %s WHERE id = %s
            """, (nuevo_hash, str(usuario_id)))
        
        conn.commit()
        return True, "Contraseña actualizada exitosamente"
    except Exception as e:
        conn.rollback()
        print(f"[DB] Error cambiando password: {e}")
        return False, f"Error al cambiar la contraseña: {e}"
    finally:
        conn.close()

def get_cdp_datos_usuario(usuario_id):
    """
    Obtiene la Casa de Paz asignada y sus líderes asociados para el usuario en sesión.
    """
    conn = get_db_connection()
    if not conn:
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
        print(f'[DB] Error al consultar datos de CDP y líderes: {e}')
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
            from mock_data import get_mock_cdp, get_mock_lideres
            mock_cdp = get_mock_cdp(1)
            mock_lideres_list = [
                {'id': 1, 'nombre': 'Mateo', 'apellido': 'Rodríguez', 'rol': 'Lider', 'telefono': '+584141234567'},
                {'id': 2, 'nombre': 'Lucía', 'apellido': 'Mendoza', 'rol': 'Sublider', 'telefono': '+584129876543'}
            ]
            mock_reps = [
                {
                    'id': f'mock-{i}',
                    'fecha': h['fecha'],
                    'fecha_formateada': h['fecha'],
                    'hr_inicio': '19:00',
                    'hr_fin': '20:30',
                    'tema': 'El Poder de la Fe',
                    'nro_regulares': 25,
                    'nro_niños': h['ninos'],
                    'nro_visitas': h['visitas'],
                    'nro_comprometidos': 5,
                    'asistencia': h['asistencia'],
                    'reconciliaciones': 1,
                    'confesiones': 2,
                    'ofrendas': h['ofrenda'],
                    'ofrendas_usd': h['ofrenda'],
                    'ofrendas_bs': 0.0,
                    'cesta_amor': 1,
                    'observaciones': h['observaciones'],
                    'lider_nombre': 'Mateo Rodríguez',
                    'iniciales': 'MR'
                }
                for i, h in enumerate(mock_cdp.get('historial', []))
            ]
            total_reps = len(mock_reps)
            start = (page - 1) * per_page
            mock_reps_page = mock_reps[start:start + per_page]
            pages = max((total_reps + per_page - 1) // per_page, 1)
            return {
                'cdp': {'id': 1, 'codigo': mock_cdp['codigo'], 'anfitrion': mock_cdp['anfitrion']},
                'lideres': mock_lideres_list,
                'metricas': {
                    'total_reportes': total_reps,
                    'asistencia_promedio': mock_cdp['promedio_historico'],
                    'ofrendas_totales': sum(r['ofrendas'] for r in mock_reps),
                    'ofrendas_usd_totales': sum(r['ofrendas'] for r in mock_reps),
                    'ofrendas_bs_totales': 0.0,
                    'visitas_totales': mock_cdp['visitas'],
                    'conversiones_totales': mock_cdp['conversiones'],
                    'reconciliaciones_totales': 4,
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
                'ofrendas_totales': 0.0,
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
                        'ofrendas_totales': 0.0,
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
        print(f"[DB] Error al cargar dashboard de líder CDP: {e}")
        return {
            'cdp': None,
            'lideres': [],
            'metricas': {
                'total_reportes': 0,
                'asistencia_promedio': 0,
                'ofrendas_totales': 0.0,
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
    """
    Valida y actualiza un reporte existente perteneciente a la CDP.
    """
    ofrendas_usd = float(form_data.get('ofrendas_usd', form_data.get('ofrendas', 0.0)) or 0.0)
    ofrendas_bs = float(form_data.get('ofrendas_bs', 0.0) or 0.0)
    datos_reporte = {
        'lider_id': form_data.get('lider_id') or None,
        'fecha': form_data.get('fecha'),
        'hr_inicio': form_data.get('hr_inicio'),
        'hr_fin': form_data.get('hr_fin'),
        'tema': form_data.get('tema', '').strip(),
        'nro_ninos': int(form_data.get('nro_ninos', 0) or 0),
        'nro_regulares': int(form_data.get('nro_regulares', 0) or 0),
        'nro_visitas': int(form_data.get('nro_visitas', 0) or 0),
        'nro_comprometidos': int(form_data.get('nro_comprometidos', 0) or 0),
        'reconciliaciones': int(form_data.get('reconciliaciones', 0) or 0),
        'confesiones': int(form_data.get('confesiones', 0) or 0),
        'ofrendas': ofrendas_usd,
        'ofrendas_usd': ofrendas_usd,
        'ofrendas_bs': ofrendas_bs,
        'cesta_amor': _parse_cesta_amor(form_data.get('cesta_amor', 0)),
        'observaciones': form_data.get('observaciones', '').strip()
    }

    conn = get_db_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    try:
        with conn.cursor() as cursor:
            exito = db_queries.actualizar_reporte_cdp(cursor, reporte_id, cdp_id, datos_reporte)
        conn.commit()

        if exito:
            try:
                invalidate_dashboard_cache()
            except Exception as cache_err:
                print(f"[WARN] No se pudo invalidar la caché: {cache_err}")
            return True, "Reporte actualizado exitosamente."
        else:
            return False, "No se encontró el reporte o no pertenece a tu Casa de Paz."
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al actualizar reporte {reporte_id}: {e}")
        return False, f"Error al guardar los cambios: {e}"
    finally:
        conn.close()


def eliminar_reporte(reporte_id, cdp_id):
    """
    Elimina de forma segura un reporte perteneciente a la CDP.
    """
    conn = get_db_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    try:
        with conn.cursor() as cursor:
            exito = db_queries.eliminar_reporte_cdp(cursor, reporte_id, cdp_id)
        conn.commit()

        if exito:
            try:
                invalidate_dashboard_cache()
            except Exception as cache_err:
                print(f"[WARN] No se pudo invalidar la caché: {cache_err}")
            return True, "Reporte eliminado exitosamente."
        else:
            return False, "No se encontró el reporte o no pertenece a tu Casa de Paz."
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error al eliminar reporte {reporte_id}: {e}")
        return False, f"Error al eliminar el reporte: {e}"
    finally:
        conn.close()


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
                # 1. Datos básicos de la CDP
                cur.execute("""
                    SELECT c.id, c.codigo, c.anfitrion, c.direccion, c.red_id,
                           r.nombre AS red_nombre,
                           COALESCE(CONCAT(u_sup.nombre, ' ', u_sup.apellido), 'Sin asignar') AS supervisor_nombre
                    FROM cdp c
                    LEFT JOIN red r ON c.red_id = r.id
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
                        tel_clean = re.sub(r'\D', '', tel)
                        # Si no empieza por código de país (ej. 0414...), ajustar para WhatsApp
                        if tel_clean.startswith('0'):
                            tel_wa = '58' + tel_clean[1:]
                        elif len(tel_clean) == 10 and not tel_clean.startswith('58'):
                            tel_wa = '58' + tel_clean
                        else:
                            tel_wa = tel_clean

                        team.append({
                            'id': l['id'],
                            'nombre_completo': f"{nom} {ape}".strip() or 'Líder',
                            'rol': l.get('rol', 'Líder'),
                            'telefono': tel,
                            'telefono_wa': tel_wa if len(tel_wa) >= 8 else None,
                            'iniciales': ini
                        })
                    
                    # Líder principal
                    lider_principal = team[0]['nombre_completo'] if team else 'Sin líder asignado'
                    telefono_contacto = team[0]['telefono'] if (team and team[0]['telefono']) else 'No registrado'
                    telefono_wa = team[0]['telefono_wa'] if (team and team[0].get('telefono_wa')) else None
                    
                    # Dirección y query para Google Maps
                    direccion = cdp.get('direccion') or 'Sector Central'
                    maps_query = urllib.parse.quote_plus(f"{direccion}, Venezuela")

                    return {
                        'id': cdp['id'],
                        'codigo': cdp['codigo'],
                        'nombre': f"Casa \"{cdp['codigo']}\"",
                        'red_nombre': cdp.get('red_nombre') or 'Red Zonal',
                        'supervisor_nombre': cdp.get('supervisor_nombre') or 'Sin supervisor',
                        'direccion': direccion,
                        'maps_url': f"https://www.google.com/maps/search/?api=1&query={maps_query}",
                        'anfitrion': cdp.get('anfitrion') or 'Sin anfitrión asignado',
                        'lider_nombre': lider_principal,
                        'telefono': telefono_contacto,
                        'telefono_wa': telefono_wa,
                        'estado': 'activa',
                        'horario': 'Martes · 7:30 PM',
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
            print(f"[DB] Error al obtener detalles de CDP {cdp_id}: {e}")
        finally:
            conn.close()
            
    # Mock / Demo fallback cuando DB no está conectada o no existe el id
    cdp_demos = {
        '1': {'codigo': 'HEB-001', 'nombre': 'Casa Bethel', 'red': 'Red Hebrón', 'dir': 'Calle 12 #18-45, sector El Carmen', 'anf': 'David Gómez y Elena Ríos', 'asist': 18, 'lider': 'Juan Carlos Pérez', 'tel': '+58 412 123 4567'},
        '2': {'codigo': 'SUR-001', 'nombre': 'Casa de Oración Sur', 'red': 'Red Sur', 'dir': 'Av. Principal #45, sector Sur', 'anf': 'María López', 'asist': 14, 'lider': 'Elena Pérez', 'tel': '+58 414 987 6543'},
        '3': {'codigo': 'CEN-001', 'nombre': 'Casa Nueva Vida', 'red': 'Red Central', 'dir': 'Carrera 8 #22-10, Centro', 'anf': 'Carlos Ramírez', 'asist': 22, 'lider': 'Andrés Soler', 'tel': '+58 424 567 8901'},
        '4': {'codigo': 'HEB-002', 'nombre': 'Casa Luz', 'red': 'Red Hebrón', 'dir': 'Calle 5 #9-14, sector Las Flores', 'anf': 'Pedro González', 'asist': 12, 'lider': 'Mateo Rodríguez', 'tel': '+58 416 345 6789'},
    }
    demo = cdp_demos.get(str(cdp_id), {
        'codigo': f'CDP-{cdp_id}', 'nombre': f'Casa "{cdp_id}"', 'red': 'Red Ministerial', 'dir': 'Ubicación comunitaria', 'anf': 'Sin anfitrión asignado', 'asist': 15, 'lider': 'Sin líder asignado', 'tel': '+58 400 000 0000'
    })
    
    return {
        'id': cdp_id,
        'codigo': demo['codigo'],
        'nombre': demo['nombre'],
        'red_nombre': demo['red'],
        'supervisor_nombre': 'Pedro González',
        'direccion': demo['dir'],
        'maps_url': f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(demo['dir'] + ', Venezuela')}",
        'anfitrion': demo['anf'],
        'lider_nombre': demo['lider'],
        'telefono': demo['tel'],
        'telefono_wa': '584121234567',
        'estado': 'activa',
        'horario': 'Martes · 7:30 PM',
        'asistencia_promedio': demo['asist'],
        'total_reportes': 12,
        'ofrendas_usd_totales': 145.50,
        'ofrendas_bs_totales': 3200.00,
        'visitas_totales': 8,
        'conversiones_totales': 5,
        'reconciliaciones_totales': 3,
        'total_voluntarios': 3,
        'lideres': [
            {'id': 1, 'nombre_completo': demo['lider'], 'rol': 'Líder principal', 'telefono': demo['tel'], 'telefono_wa': '584121234567', 'iniciales': 'LP'},
            {'id': 2, 'nombre_completo': demo['anf'], 'rol': 'Anfitrión', 'telefono': '+58 414 111 2233', 'telefono_wa': '584141112233', 'iniciales': 'AN'},
            {'id': 3, 'nombre_completo': 'Daniel Morales', 'rol': 'Apoyo comunitario', 'telefono': '+58 424 333 4455', 'telefono_wa': '584243334455', 'iniciales': 'DM'},
        ],
        'reportes': [
            {
                'id': 1,
                'fecha_formateada': '24 Ago 2026',
                'tema': 'El Poder de la Fe y Unidad',
                'asistencia': 18,
                'nro_regulares': 10,
                'nro_niños': 4,
                'nro_visitas': 3,
                'nro_comprometidos': 1,
                'ofrendas_usd': 25.0,
                'ofrendas_bs': 450.0,
                'cesta_amor': 1,
                'observaciones': 'Excelente participación de nuevas familias del sector.',
                'lider_nombre': demo['lider'],
                'iniciales': 'LP'
            },
            {
                'id': 2,
                'fecha_formateada': '17 Ago 2026',
                'tema': 'Creciendo en Sabiduría',
                'asistencia': 16,
                'nro_regulares': 9,
                'nro_niños': 3,
                'nro_visitas': 2,
                'nro_comprometidos': 2,
                'ofrendas_usd': 20.0,
                'ofrendas_bs': 380.0,
                'cesta_amor': 1,
                'observaciones': 'Se entregó material de apoyo para el próximo ciclo.',
                'lider_nombre': demo['lider'],
                'iniciales': 'LP'
            },
            {
                'id': 3,
                'fecha_formateada': '10 Ago 2026',
                'tema': 'Sembrando Amor en la Comunidad',
                'asistencia': 20,
                'nro_regulares': 12,
                'nro_niños': 5,
                'nro_visitas': 3,
                'nro_comprometidos': 0,
                'ofrendas_usd': 30.0,
                'ofrendas_bs': 520.0,
                'cesta_amor': 1,
                'observaciones': 'Acompañamiento especial del equipo de supervisión.',
                'lider_nombre': demo['lider'],
                'iniciales': 'LP'
            }
        ]
    }