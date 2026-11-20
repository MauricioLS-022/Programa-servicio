"""
Script idempotente de migración de integridad relacional para la base de datos `serv_comunitario`.

Alinea el esquema MySQL/MariaDB con el contrato canónico definido en REQUERIMIENTOS.md:
1. `cdp.usuario_id`: CHAR(36) NULL DEFAULT NULL + `fk_cdp_usuario` con `ON DELETE SET NULL ON UPDATE CASCADE`
   (permite desvincular cuentas de usuario sin lanzar IntegrityError 1048 ni borrar CDPs en cascada).
2. `reporte.fk_reporte_cdp`: `ON DELETE RESTRICT ON UPDATE CASCADE`
   (protege el historial de reportes contra borrados físicos accidentales de Casas de Paz).
3. `reporte`: índice único `uq_cdp_fecha (cdp_id, fecha)`
   (candado de unicidad real a nivel de BD contra envíos duplicados concurrentes).

Uso:
    python backend/scripts/migrate_schema_integrity.py --dry-run
    python backend/scripts/migrate_schema_integrity.py
    python backend/scripts/migrate_schema_integrity.py --dedupe
"""
import argparse
import os
import sys
import pymysql

# Asegurar acceso a backend/config.py
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from config import Config  # noqa: E402


def _connect():
    use_ssl = Config.DB_SSL and Config.DB_HOST not in ('localhost', '127.0.0.1')
    ssl_kwargs = {'ssl': {'ssl_mode': 'REQUIRED'}} if use_ssl else {}
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=False,
        **ssl_kwargs,
    )


def _get_column_info(cur, db_name: str, table: str, column: str):
    cur.execute(
        """
        SELECT IS_NULLABLE, COLUMN_TYPE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (db_name, table, column),
    )
    return cur.fetchone()


def _get_fk_rule(cur, db_name: str, table: str, constraint_name: str):
    cur.execute(
        """
        SELECT CONSTRAINT_NAME, UPDATE_RULE, DELETE_RULE
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = %s AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s
        """,
        (db_name, table, constraint_name),
    )
    return cur.fetchone()


def _has_unique_cdp_fecha(cur, db_name: str) -> bool:
    cur.execute(
        """
        SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS cols
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'reporte' AND NON_UNIQUE = 0
        GROUP BY INDEX_NAME
        """,
        (db_name,),
    )
    for row in cur.fetchall() or []:
        if (row.get('cols') or '').lower() == 'cdp_id,fecha':
            return True
    return False


def _find_duplicate_reports(cur):
    cur.execute(
        """
        SELECT cdp_id, fecha, COUNT(*) AS cnt
        FROM reporte
        GROUP BY cdp_id, fecha
        HAVING COUNT(*) > 1
        ORDER BY cdp_id, fecha
        """
    )
    return cur.fetchall() or []


def plan_and_apply(dry_run: bool = False, dedupe: bool = False) -> int:
    db_name = Config.DB_NAME
    conn = _connect()
    planned_statements: list[tuple[str, str]] = []

    try:
        with conn.cursor() as cur:
            # 1. cdp.usuario_id nullable + fk_cdp_usuario ON DELETE SET NULL
            col_uid = _get_column_info(cur, db_name, 'cdp', 'usuario_id')
            fk_cdp_uid = _get_fk_rule(cur, db_name, 'cdp', 'fk_cdp_usuario')
            needs_uid_alter = (
                col_uid is not None and col_uid.get('IS_NULLABLE') != 'YES'
            ) or (
                fk_cdp_uid is None or fk_cdp_uid.get('DELETE_RULE') != 'SET NULL'
            )
            if needs_uid_alter:
                if fk_cdp_uid:
                    planned_statements.append((
                        "Eliminar FK legacy fk_cdp_usuario",
                        "ALTER TABLE `cdp` DROP FOREIGN KEY `fk_cdp_usuario`",
                    ))
                planned_statements.append((
                    "Permitir NULL en cdp.usuario_id",
                    "ALTER TABLE `cdp` MODIFY COLUMN `usuario_id` CHAR(36) DEFAULT NULL",
                ))
                planned_statements.append((
                    "Recrear fk_cdp_usuario con ON DELETE SET NULL",
                    "ALTER TABLE `cdp` ADD CONSTRAINT `fk_cdp_usuario` "
                    "FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) "
                    "ON DELETE SET NULL ON UPDATE CASCADE",
                ))

            # 2. reporte.fk_reporte_cdp ON DELETE RESTRICT
            fk_rep_cdp = _get_fk_rule(cur, db_name, 'reporte', 'fk_reporte_cdp')
            if fk_rep_cdp is None or fk_rep_cdp.get('DELETE_RULE') != 'RESTRICT':
                if fk_rep_cdp:
                    planned_statements.append((
                        "Eliminar FK legacy fk_reporte_cdp",
                        "ALTER TABLE `reporte` DROP FOREIGN KEY `fk_reporte_cdp`",
                    ))
                planned_statements.append((
                    "Recrear fk_reporte_cdp con ON DELETE RESTRICT",
                    "ALTER TABLE `reporte` ADD CONSTRAINT `fk_reporte_cdp` "
                    "FOREIGN KEY (`cdp_id`) REFERENCES `cdp` (`id`) "
                    "ON DELETE RESTRICT ON UPDATE CASCADE",
                ))

            # 3. UNIQUE KEY uq_cdp_fecha (cdp_id, fecha)
            has_uq = _has_unique_cdp_fecha(cur, db_name)
            dups = []
            if not has_uq:
                dups = _find_duplicate_reports(cur)
                if dups and not dedupe:
                    print("[WARN] Se detectaron reportes duplicados para (cdp_id, fecha):")
                    for d in dups:
                        print(f"  - cdp_id={d['cdp_id']} fecha={d['fecha']} count={d['cnt']}")
                    print("Ejecuta con --dedupe para conservar el registro más reciente y eliminar duplicados antes de crear uq_cdp_fecha.")
                    if not dry_run:
                        return 2
                planned_statements.append((
                    "Agregar índice único uq_cdp_fecha (cdp_id, fecha) en reporte",
                    "ALTER TABLE `reporte` ADD UNIQUE KEY `uq_cdp_fecha` (`cdp_id`, `fecha`)",
                ))

            if not planned_statements:
                print(f"[OK] El esquema de '{db_name}' ya cumple todas las restricciones canónicas.")
                return 0

            print(f"[PLAN] {len(planned_statements)} cambio(s) sobre '{db_name}':")
            for idx, (desc, sql) in enumerate(planned_statements, start=1):
                print(f"  {idx}. {desc}\n     SQL: {sql}")

            if dry_run:
                print("[DRY-RUN] No se aplicaron cambios en la base de datos.")
                return 0

            if dups and dedupe:
                print(f"[DEDUPE] Eliminando duplicados en {len(dups)} grupo(s) (conservando el mayor ID)...")
                for d in dups:
                    cur.execute(
                        "SELECT id FROM reporte WHERE cdp_id = %s AND fecha = %s ORDER BY id DESC",
                        (d['cdp_id'], d['fecha']),
                    )
                    rows = cur.fetchall() or []
                    for stale in rows[1:]:
                        cur.execute("DELETE FROM reporte WHERE id = %s", (stale['id'],))
                conn.commit()

            for desc, sql in planned_statements:
                print(f"[APPLY] {desc}...")
                cur.execute(sql)
            conn.commit()
            print(f"[OK] Migración de integridad completada exitosamente sobre '{db_name}'.")
            return 0
    except Exception as exc:
        conn.rollback()
        print(f"[ERROR] Fallo durante la migración: {exc}")
        return 1
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migración idempotente de integridad referencial y unicidad para serv_comunitario."
    )
    parser.add_argument("--dry-run", action="store_true", help="Muestra las sentencias DDL sin ejecutarlas.")
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Elimina reportes duplicados por (cdp_id, fecha) antes de crear uq_cdp_fecha.",
    )
    args = parser.parse_args()
    sys.exit(plan_and_apply(dry_run=args.dry_run, dedupe=args.dedupe))


if __name__ == '__main__':
    main()
