"""
Servicio de Casa de Paz (CDP) - Lógica de negocio para reportes y perfiles.
"""
from flask import request
from database import get_db_connection
from utils.cache import invalidate_dashboard_cache
import db_queries

def process_reporte(cdp_id, form_data):
    """
    Valida y procesa el guardado de un reporte de Casa de Paz.
    """
    # 1. Preparación y conversión de datos (incluye los campos de reportes)
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
        'ofrendas': float(form_data.get('ofrendas', 0.0) or 0.0),
        'cesta_amor': float(form_data.get('cesta_amor', 0.0) or 0.0),
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


def update_perfil(usuario_id, nombre, apellido, email):
    """
    Actualiza los datos del perfil del usuario.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn:
        return False, "No hay conexión a la base de datos"
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario 
                SET nombre = %s, apellido = %s, email = %s
                WHERE id = %s
            """, (nombre, apellido, email, str(usuario_id)))
        conn.commit()
        return True, "Perfil actualizado exitosamente"
    except Exception as e:
        conn.rollback()  # Se agrega rollback para deshacer transacciones fallidas
        print(f"[DB] Error actualizando perfil: {e}")
        return False, f"Error al actualizar perfil: {e}"
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