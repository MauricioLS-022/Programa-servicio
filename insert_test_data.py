import pymysql
from datetime import date, timedelta

conn = pymysql.connect(host='localhost', user='root', password='', database='serv_comunitario')
cur = conn.cursor()

# 1. Crear una red
cur.execute("INSERT INTO red (id, nombre, supervisor_id) VALUES (1, 'Cielos Abiertos', 'ca58cfc6-8337-11f1-8217-2016d8516279')")
print('✅ Red creada')

# 2. Crear CDPs
cur.execute("INSERT INTO cdp (codigo, anfitrion, telefono, direccion, red_id, usuario_id) VALUES ('CDP-001', 'Juan Pérez', '1234567890', 'Calle 1 #10-20', 1, '1d4f7c99-7d51-11f1-bf9e-2016d8516279')")
cur.execute("INSERT INTO cdp (codigo, anfitrion, telefono, direccion, red_id, usuario_id) VALUES ('CDP-002', 'Maria López', '0987654321', 'Calle 2 #30-40', 1, '1d4f7c99-7d51-11f1-bf9e-2016d8516279')")
print('✅ CDPs creados')

# 3. Crear líderes
cur.execute("INSERT INTO lider (nombre, apellido, rol, telefono, cdp_id) VALUES ('Pedro', 'García', 'Lider', '1111111111', 1)")
cur.execute("INSERT INTO lider (nombre, apellido, rol, telefono, cdp_id) VALUES ('Ana', 'Martínez', 'Sublider', '2222222222', 2)")
print('✅ Líderes creados')

# 4. Crear reportes de prueba
fechas = [date.today() - timedelta(days=i*7) for i in range(5)]
for i, fecha in enumerate(fechas):
    cur.execute('''INSERT INTO reporte 
        (nro_niños, nro_regulares, nro_visitas, nro_comprometidos, reconciliaciones, confesiones, cesta_amor, fecha, hr_inicio, hr_fin, tema, observaciones, ofrendas, cdp_id, enviado_por_lider_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (5+i, 15+i, 3+i, 2+i, 1, 0, 1, fecha, '19:00:00', '21:00:00', f'Reunión {i+1}', 'Todo bien', 150.00, 1, 1)
    )
print('✅ Reportes creados')

conn.commit()
print('🎉 Datos de prueba insertados correctamente')
conn.close()