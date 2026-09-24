"""
Script de depuración segura de reportes duplicados en la base de datos MySQL.
Detecta grupos con la misma Casa de Paz y fecha, conserva el registro más reciente
y elimina los clones idénticos redundantes.
"""
import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import get_db_connection
from utils.cache import invalidate_dashboard_cache

def depurar_reportes_duplicados(dry_run=False):
    with app.app_context():
        conn = get_db_connection()
        if not conn:
            print("[ERROR] No se pudo conectar a la base de datos.")
            return False

        try:
            with conn.cursor() as cur:
                # 1. Detectar grupos con duplicados por Casa de Paz y Fecha
                cur.execute("""
                    SELECT cdp_id, fecha, COUNT(*) AS cantidad
                    FROM reporte
                    GROUP BY cdp_id, fecha
                    HAVING COUNT(*) > 1
                """)
                grupos = cur.fetchall() or []

                if not grupos:
                    print("[OK] No se encontraron reportes duplicados en la base de datos.")
                    return True

                print(f"[INFO] Se detectaron {len(grupos)} grupos de reportes con duplicados.")

                total_eliminados = 0
                for g in grupos:
                    cdp_id = g['cdp_id']
                    fecha = g['fecha']

                    # Obtener todos los reportes de este grupo ordenados
                    cur.execute("""
                        SELECT id, tema, fecha, nro_regulares
                        FROM reporte
                        WHERE cdp_id = %s AND fecha = %s
                        ORDER BY id DESC
                    """, (cdp_id, fecha))
                    filas = cur.fetchall() or []

                    if len(filas) <= 1:
                        continue

                    # Conservar el primero, eliminar los restantes
                    conservar = filas[0]
                    eliminar = filas[1:]

                    ids_a_borrar = [r['id'] for r in eliminar]
                    print(f" -> CDP {cdp_id} | Fecha {fecha}: Conservando ID '{conservar['id'][:8]}...', eliminando {len(ids_a_borrar)} clon(es).")

                    total_eliminados += len(ids_a_borrar)
                    if not dry_run:
                        format_strings = ','.join(['%s'] * len(ids_a_borrar))
                        cur.execute(f"DELETE FROM reporte WHERE id IN ({format_strings})", tuple(ids_a_borrar))

                if not dry_run:
                    conn.commit()
                    print(f"\n[ÉXITO] Depuración completada. Se eliminaron {total_eliminados} registros duplicados.")
                    try:
                        invalidate_dashboard_cache()
                        print("[OK] Caché del dashboard invalidada correctamente.")
                    except Exception as err:
                        print(f"[WARN] No se pudo invalidar caché: {err}")
                else:
                    print(f"\n[DRY RUN] Se habrían eliminado {total_eliminados} registros duplicados (sin cambios en BD).")

            return True
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Ocurrió un fallo durante la depuración: {e}")
            return False
        finally:
            conn.close()

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    depurar_reportes_duplicados(dry_run=dry)
