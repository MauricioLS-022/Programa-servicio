"""
Servicio de Casa de Paz (CDP) - Lógica de negocio para reportes y perfiles.
"""
from flask import request
from database import get_db_connection
from utils.cache import invalidate_dashboard_cache


def process_reporte(anfitrion, ninos, regulares, visitas, comprometidos, asistencia,
                   reconciliaciones, confesiones, cesta, fecha, horaini, horafin,
                   tema, observaciones, ofrendas):
    """
    Procesa un reporte enviado por un CDP.
    Invalidar la caché del dashboard después de guardar.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    val = (anfitrion, ninos, regulares, visitas, comprometidos, asistencia,
           reconciliaciones, confesiones, cesta, fecha, horaini, horafin,
           tema, observaciones, ofrendas)
    print(val)
    
    conn = get_db_connection()
    if not conn:
        # Modo demo - solo registra en logs
        invalidate_dashboard_cache()
        return True, "Reporte guardado en modo demo"
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reporte 
            (anfitrion, ninos, regulares, visitas, comprometidos, asistencia,
             reconciliaciones, confesiones, cesta, fecha, horaini, horafin,
             tema, observaciones, ofrendas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, val)
        conn.commit()
        cur.close()
        
        # Invalidar caché del dashboard
        invalidate_dashboard_cache()
        
        return True, "Reporte guardado exitosamente"
    except Exception as e:
        print(f"[DB] Error guardando reporte: {e}")
        return False, f"Error al guardar reporte: {e}"
    finally:
        conn.close()


def get_perfil_data(usuario_id):
    """
    Obtiene los datos del perfil del usuario.
    
    Returns:
        dict con los datos del perfil
    """
    conn = get_db_connection()
    perfil_data = {}
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, username, nombre, apellido, email, tipo_usuario
                FROM usuario 
                WHERE id = %s
            """, (str(usuario_id),))
            perfil_data = cur.fetchone() or {}
            cur.close()
        except Exception as e:
            print(f"[DB] Error perfil: {e}")
        finally:
            conn.close()
    
    return perfil_data


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
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuario 
            SET nombre = %s, apellido = %s, email = %s
            WHERE id = %s
        """, (nombre, apellido, email, str(usuario_id)))
        conn.commit()
        cur.close()
        return True, "Perfil actualizado exitosamente"
    except Exception as e:
        print(f"[DB] Error actualizando perfil: {e}")
        return False, f"Error al actualizar perfil: {e}"
    finally:
        conn.close()