import uuid
import os
import sys
from datetime import date, timedelta
import pymysql
from werkzeug.security import generate_password_hash

# Asegurar codificación utf-8 en consola si está disponible
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configuración de base de datos (con soporte a variables de entorno)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'serv_comunitario')

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def poblar_datos():
    conn = get_connection()
    cur = conn.cursor()
    print("[*] Iniciando insercion de datos de prueba...")

    try:
        # -------------------------------------------------------------
        # 1. USUARIOS DE PRUEBA
        # -------------------------------------------------------------
        usuarios_data = [
            {
                'id': '702f2129-7d4e-11f1-bf9e-2016d8516279',
                'username': 'admin',
                'password': generate_password_hash('admin'),
                'tipo_usuario': 'admin',
                'nombre': 'Mauricio',
                'apellido': 'Leal'
            },
            {
                'id': 'ca58cfc6-8337-11f1-8217-2016d8516279',
                'username': 'super',
                'password': generate_password_hash('supervisor'),
                'tipo_usuario': 'supervisor',
                'nombre': 'Carlos',
                'apellido': 'Mendoza'
            },
            {
                'id': 'da59cfc6-8337-11f1-8217-2016d8516279',
                'username': 'super2',
                'password': generate_password_hash('supervisor'),
                'tipo_usuario': 'supervisor',
                'nombre': 'Patricia',
                'apellido': 'Morales'
            },
            {
                'id': 'ea59cfc6-8337-11f1-8217-2016d8516279',
                'username': 'super3',
                'password': generate_password_hash('supervisor'),
                'tipo_usuario': 'supervisor',
                'nombre': 'Roberto',
                'apellido': 'Navas'
            },
            {
                'id': '1d4f7c99-7d51-11f1-bf9e-2016d8516279',
                'username': 'lider',
                'password': generate_password_hash('lider'),
                'tipo_usuario': 'lider_cdp',
                'nombre': 'Mauricio',
                'apellido': 'Leal'
            },
            {
                'id': '2e59be2e-a1c3-11f1-8110-2016d8516279',
                'username': 'lider2',
                'password': generate_password_hash('lider'),
                'tipo_usuario': 'lider_cdp',
                'nombre': 'Felipe',
                'apellido': 'Gutiérrez'
            },
            {
                'id': '2e59db50-a1c3-11f1-8110-2016d8516279',
                'username': 'lider3',
                'password': generate_password_hash('lider'),
                'tipo_usuario': 'lider_cdp',
                'nombre': 'María',
                'apellido': 'Márquez'
            },
            {
                'id': '3f60ec61-b2d4-11f1-9221-2016d8516279',
                'username': 'lider4',
                'password': generate_password_hash('lider'),
                'tipo_usuario': 'lider_cdp',
                'nombre': 'Andrés',
                'apellido': 'Soler'
            }
        ]

        for u in usuarios_data:
            cur.execute("""
                INSERT INTO usuario (id, username, password, tipo_usuario, is_active, nombre, apellido)
                VALUES (%s, %s, %s, %s, 1, %s, %s)
                ON DUPLICATE KEY UPDATE
                    password = VALUES(password),
                    tipo_usuario = VALUES(tipo_usuario),
                    nombre = VALUES(nombre),
                    apellido = VALUES(apellido),
                    is_active = 1
            """, (u['id'], u['username'], u['password'], u['tipo_usuario'], u['nombre'], u['apellido']))
        print("[OK] Usuarios asegurados (admin, super, super2, super3, lider, lider2, lider3, lider4)")

        # -------------------------------------------------------------
        # 2. REDES (Cada red con supervisor único - Relación 1 a 1)
        # -------------------------------------------------------------
        redes_data = [
            (1, 'Cielos Abiertos', 'ca58cfc6-8337-11f1-8217-2016d8516279'),
            (2, 'Red Sur', 'da59cfc6-8337-11f1-8217-2016d8516279'),
            (3, 'Red Central', 'ea59cfc6-8337-11f1-8217-2016d8516279'),
        ]

        for red_id, nombre, sup_id in redes_data:
            cur.execute("""
                INSERT INTO red (id, nombre, is_active, supervisor_id)
                VALUES (%s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = VALUES(nombre),
                    is_active = 1,
                    supervisor_id = VALUES(supervisor_id)
            """, (red_id, nombre, sup_id))
        print("[OK] Redes creadas / actualizadas (Cielos Abiertos, Red Sur, Red Central)")

        # -------------------------------------------------------------
        # 3. CASAS DE PAZ (CDPs)
        # -------------------------------------------------------------
        cdps_data = [
            (1, 'CA-3.1', 'Felipe Gutiérrez', '04245566320', 'Av. Guarapiche #12', 1, '2e59be2e-a1c3-11f1-8110-2016d8516279'),
            (2, 'CA-3.2', 'María Márquez', '04124567896', 'Unare II, Manzana 15', 1, '2e59db50-a1c3-11f1-8110-2016d8516279'),
            (3, 'SUR-001', 'Roberto Gómez', '04141234567', 'Calle Principal Sur #45', 2, '1d4f7c99-7d51-11f1-bf9e-2016d8516279'),
            (4, 'CEN-001', 'Elena Sánchez', '04169998877', 'Casco Central, Calle Bolívar', 3, '3f60ec61-b2d4-11f1-9221-2016d8516279'),
        ]

        for cdp_id, codigo, anfitrion, telefono, direccion, red_id, user_id in cdps_data:
            cur.execute("""
                INSERT INTO cdp (id, codigo, anfitrion, telefono, direccion, is_active, red_id, usuario_id)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
                ON DUPLICATE KEY UPDATE
                    codigo = VALUES(codigo),
                    anfitrion = VALUES(anfitrion),
                    telefono = VALUES(telefono),
                    direccion = VALUES(direccion),
                    is_active = 1,
                    red_id = VALUES(red_id),
                    usuario_id = VALUES(usuario_id)
            """, (cdp_id, codigo, anfitrion, telefono, direccion, red_id, user_id))
        print("[OK] Casas de Paz creadas / actualizadas (CA-3.1, CA-3.2, SUR-001, CEN-001)")

        # -------------------------------------------------------------
        # 4. LÍDERES
        # -------------------------------------------------------------
        lideres_data = [
            (1, 'Pedro', 'García', 'Lider', '04241112233', 1),
            (2, 'Ana', 'Martínez', 'Sublider', '04124445566', 1),
            (3, 'Mateo', 'Rodríguez', 'Lider', '04147778899', 2),
            (4, 'Sofía', 'Hernández', 'Sublider', '04263332211', 2),
            (5, 'Andrés', 'Soler', 'Lider', '04165554433', 3),
            (6, 'Elena', 'Pérez', 'Lider', '04128889900', 4),
        ]

        for lid_id, nom, ape, rol, tel, c_id in lideres_data:
            cur.execute("""
                INSERT INTO lider (id, nombre, apellido, rol, telefono, is_active, cdp_id)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = VALUES(nombre),
                    apellido = VALUES(apellido),
                    rol = VALUES(rol),
                    telefono = VALUES(telefono),
                    is_active = 1,
                    cdp_id = VALUES(cdp_id)
            """, (lid_id, nom, ape, rol, tel, c_id))
        print("[OK] Líderes creados / actualizados")

        # -------------------------------------------------------------
        # 5. REPORTES DE PRUEBA HISTÓRICOS
        # -------------------------------------------------------------
        temas = [
            'El Poder de la Fe',
            'Caminando en Bendición',
            'Amor y Unidad Fraternal',
            'Victoria en la Prueba',
            'Multiplicación y Servicio',
            'La Gracia Transformadora',
            'Sanidad y Restauración',
            'Esperanza Viva',
        ]

        hoy = date.today()
        # Asegurar columnas bimoneda en tabla reporte
        try:
            cur.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_usd'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE reporte ADD COLUMN ofrendas_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER ofrendas")
            cur.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_bs'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE reporte ADD COLUMN ofrendas_bs DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER ofrendas_usd")
        except Exception as e:
            print(f"[!] Aviso al verificar/crear columnas de ofrendas: {e}")

        # Generar reportes para las últimas 8 semanas en varias CDPs
        reportes_creados = 0
        for semana_idx in range(8):
            fecha_reporte = hoy - timedelta(days=semana_idx * 7)
            
            # Insertar para CDP 1 (Líder 1)
            tema_1 = temas[semana_idx % len(temas)]
            usd_1 = round(20.0 + (semana_idx * 5.0), 2)
            bs_1 = round(280.0 + (semana_idx * 50.0), 2)
            cur.execute("""
                INSERT INTO reporte (
                    id, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
                    reconciliaciones, confesiones, cesta_amor, fecha, hr_inicio, hr_fin,
                    tema, observaciones, ofrendas, ofrendas_usd, ofrendas_bs, cdp_id, enviado_por_lider_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                str(uuid.uuid4()),
                4 + (semana_idx % 3),
                12 + (semana_idx * 2),
                2 + (semana_idx % 4),
                3 + (semana_idx % 2),
                1 if semana_idx % 2 == 0 else 0,
                1 if semana_idx % 3 == 0 else 0,
                1,
                fecha_reporte,
                '19:00:00',
                '20:30:00',
                f'{tema_1} (Semana {8 - semana_idx})',
                'Reunión llena de bendición y comunión.',
                usd_1,
                usd_1,
                bs_1,
                1,
                1
            ))
            reportes_creados += 1

            # Insertar para CDP 2 (Líder 3)
            if semana_idx < 6:
                tema_2 = temas[(semana_idx + 2) % len(temas)]
                usd_2 = round(15.0 + (semana_idx * 4.0), 2)
                bs_2 = round(210.0 + (semana_idx * 40.0), 2)
                cur.execute("""
                    INSERT INTO reporte (
                        id, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
                        reconciliaciones, confesiones, cesta_amor, fecha, hr_inicio, hr_fin,
                        tema, observaciones, ofrendas, ofrendas_usd, ofrendas_bs, cdp_id, enviado_por_lider_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    3 + (semana_idx % 2),
                    10 + semana_idx,
                    1 + (semana_idx % 3),
                    2,
                    0,
                    1 if semana_idx % 2 == 1 else 0,
                    0,
                    fecha_reporte,
                    '18:30:00',
                    '20:00:00',
                    f'{tema_2} (Grupo Sur)',
                    'Buena participación de los asistentes.',
                    usd_2,
                    usd_2,
                    bs_2,
                    2,
                    3
                ))
                reportes_creados += 1

            # Insertar para CDP 3 (Líder 5)
            if semana_idx < 4:
                tema_3 = temas[(semana_idx + 4) % len(temas)]
                usd_3 = round(25.0 + (semana_idx * 6.0), 2)
                bs_3 = round(350.0 + (semana_idx * 60.0), 2)
                cur.execute("""
                    INSERT INTO reporte (
                        id, nro_niños, nro_regulares, nro_visitas, nro_comprometidos,
                        reconciliaciones, confesiones, cesta_amor, fecha, hr_inicio, hr_fin,
                        tema, observaciones, ofrendas, ofrendas_usd, ofrendas_bs, cdp_id, enviado_por_lider_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    str(uuid.uuid4()),
                    6 + semana_idx,
                    15 + semana_idx,
                    4,
                    3,
                    1,
                    2,
                    1,
                    fecha_reporte,
                    '19:00:00',
                    '20:30:00',
                    f'{tema_3} (Red Sur)',
                    'Gran tiempo de ministración.',
                    usd_3,
                    usd_3,
                    bs_3,
                    3,
                    5
                ))
                reportes_creados += 1

        print(f"[OK] {reportes_creados} reportes historicos de prueba insertados con exito")

        conn.commit()
        print("\n[SUCCESS] Todos los datos de prueba han sido insertados y sincronizados correctamente.")
        print("Credenciales de acceso disponibles:")
        print("   - Admin:      usuario: admin  | clave: admin")
        print("   - Supervisor: usuario: super  | clave: supervisor")
        print("   - Líder CDP:  usuario: lider  | clave: lider")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Error durante la insercion de datos: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    poblar_datos()