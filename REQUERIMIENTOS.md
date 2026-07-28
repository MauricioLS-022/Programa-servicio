# Requerimientos — Proyecto Vino Nuevo

## Descripción General
Aplicación web de gestión y reportes para un servicio comunitario (ministerio "Vino Nuevo").  
**Stack:** Python Flask + MySQL (PyMySQL) + HTML/CSS (Jinja2)

---

## 1. Requerimientos Faltantes (Backend no implementado)

| # | Requerimiento | Estado | Detalle |
|---|---|---|---|
| 1 | **INSERT de reportes en BD** | ❌ No funciona | `app.py:54-56` — Captura los datos del form pero nunca ejecuta `INSERT INTO`. Solo hace `print(val)` |
| 2 | **CRUD de Usuarios** | ❌ No funciona | Las rutas `/admin/usuarios`, `/admin/usuarios/editar` solo renderizan HTML estático. No hay consultas a BD |
| 3 | **CRUD de Casas de Paz** | ❌ No funciona | `/admin/casa_de_paz/editar` no consulta ni modifica la BD |
| 4 | **CRUD de Redes** | ❌ No funciona | `/admin/red/editar` igual, solo HTML estático |
| 5 | **CRUD de Líderes** | ❌ No funciona | `/admin/lider/editar` solo HTML estático |
| 6 | **Dashboard con datos reales** | ❌ Datos hardcodeados | `dashboard_admin.html` muestra números fijos (1,248 reportes, 86 usuarios, etc.) |
| 7 | **Vista "Reportes enviados"** | ❌ Vacía | `index.html` extiende `layout.html` pero el block `content` está vacío |
| 8 | **Filtros de reportes** | ❌ No funcionan | Los filtros de fecha/líder en `reportes_admin.html` no tienen backend |
| 9 | **Paginación real** | ❌ No implementada | Los controles de paginación son decorativos |
| 10 | **Exportar PDF/Excel** | ❌ No implementado | Botones existen en el HTML pero no hacen nada |
| 11 | **Búsqueda en tiempo real** | ❌ No implementada | El ícono de búsqueda en usuarios/estructura es decorativo |
| 12 | **Flash messages (notificaciones)** | ❌ No implementado | No hay feedback al crear/editar/eliminar |
| 13 | **Contactar por WhatsApp** | ❌ No implementado | Botón "Contactar" en alertas no tiene funcionalidad |
| 14 | **Gestión de contraseña** | ❌ No implementado | No se puede cambiar contraseña desde perfil |
| 15 | **Rol "supervisor" sin vistas** | ❌ Sin implementar | El rol existe pero no tiene rutas propias (excepto perfil) |

---

## 2. Problemas de Seguridad

| # | Problema | Severidad | Detalle |
|---|---|---|---|
| 1 | **Contraseñas en texto plano** | 🔴 Crítica | `app.py:125` — Compara passwords directamente, sin hash |
| 2 | **Sin CSRF protection** | 🔴 Alta | Los formularios POST no tienen token CSRF |
| 3 | **Credenciales de BD hardcodeadas** | 🟡 Media | `app.py:26,51,64,75,122` — Usuario root sin contraseña |
| 4 | **Conexiones BD sin cerrar** | 🟡 Media | Nunca se hace `connect.close()` ni `C.close()` |
| 5 | **`debug=True` en producción** | 🟡 Media | `app.py:145` — Expone traceback completo |

---

## 3. Mejoras UI/UX

| # | Mejora | Prioridad | Detalle |
|---|---|---|---|
| 1 | **index.html vacío** | Alta | La home del líder CDP no muestra nada (ni reportes enviados, ni resumen) |
| 2 | **Responsive en móviles** | Alta | Las tablas de usuarios/reportes no tienen `overflow-x: auto` |
| 3 | **Estados vacíos** | Media | Cuando no hay datos, mostrar mensaje amigable en vez de tabla vacía |
| 4 | **Feedback de botones copiar** | Media | Los iconos de copiar usuario/contraseña no tienen JS |
| 5 | **Tooltips en gráfico donut** | Media | El gráfico del dashboard no muestra tooltips al hacer hover |
| 6 | **Eliminar barra de progreso lineal** | Baja | El dashboard tiene dos medidores para el mismo dato |
| 7 | **Filtros de búsqueda en tiempo real** | Media | Implementar JS para filtrar tablas sin recargar |
| 8 | **Adaptar sidebar en móvil** | Media | La barra de navegación del líder se rompe en pantallas pequeñas |
| 9 | **CSS duplicado** | Baja | `style.css` y `admin/admin.css` comparten variables y estilos repetidos |
| 10 | **Inconsistentes de naming** | Baja | Archivos con espacios ("generar reporte.html") dificultan mantenimiento |

---

## 4. Estructura de Base de Datos Requerida

Basado en los formularios, se necesitan estas tablas en `serv_comunitario`:

```sql
CREATE TABLE usuario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('admin', 'supervisor', 'cdp') NOT NULL
);

CREATE TABLE red (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    supervisor_id INT,
    FOREIGN KEY (supervisor_id) REFERENCES usuario(id)
);

CREATE TABLE casa_de_paz (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    red_id INT NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (red_id) REFERENCES red(id)
);

CREATE TABLE lider (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    rol ENUM('Lider', 'Sublider') NOT NULL,
    cdp_id INT NOT NULL,
    FOREIGN KEY (cdp_id) REFERENCES casa_de_paz(id)
);

CREATE TABLE reporte (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cdp_id INT NOT NULL,
    anfitrion VARCHAR(150) NOT NULL,
    ninos INT DEFAULT 0,
    regulares INT DEFAULT 0,
    visitas INT DEFAULT 0,
    comprometidos INT DEFAULT 0,
    asistencia INT DEFAULT 0,
    reconciliaciones INT DEFAULT 0,
    confesiones INT DEFAULT 0,
    cesta VARCHAR(255),
    fecha DATE NOT NULL,
    horaini TIME NOT NULL,
    horafin TIME NOT NULL,
    tema VARCHAR(255),
    observaciones TEXT,
    ofrendas DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (cdp_id) REFERENCES casa_de_paz(id)
);
```

---

## 5. Priorización por Fases

### Fase 1 — Core funcional
1. Crear tablas en BD y relaciones
2. Implementar INSERT de reportes
3. Implementar login con passwords hasheados (bcrypt/werkzeug)
4. Cerrar conexiones de BD correctamente (usar context managers o try/finally)

### Fase 2 — CRUD completo
5. CRUD Usuarios (listar, crear, editar, eliminar)
6. CRUD Casas de Paz
7. CRUD Redes
8. CRUD Líderes

### Fase 3 — Dashboard y reportes
9. Dashboard con datos reales (consultas agregadas)
10. Filtros funcionales
11. Paginación real

### Fase 4 — UX y polish
12. Flash messages
13. Estados vacíos
14. Responsive completo
15. Exportar PDF/Excel
16. Búsqueda en tiempo real
