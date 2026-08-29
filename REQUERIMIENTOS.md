# Requerimientos — Proyecto Vino Nuevo

## Descripción General
Aplicación web de gestión y reportes para un servicio comunitario (ministerio "Vino Nuevo").  
**Stack:** Python Flask + MySQL (PyMySQL) + HTML/CSS (Jinja2)

---

## 1. Estado general de requerimientos

**Criterio:** Se considera implementado solo lo que está conectado a una ruta, servicio, consulta o listener funcional. El HTML estático por sí solo se considera maquetado.

| # | Requerimiento | Estado actual | Evidencia y trabajo pendiente |
|---|---|---|---|
| 1 | **INSERT de reportes en BD** | ✅ Implementado | `services/cdp_service.py` y `db_queries.insertar_reporte()` alineados con el esquema SQL (`nro_niños`, `nro_regulares`, `nro_visitas`, `nro_comprometidos`, `reconciliaciones`, `confesiones`, `cesta_amor`, `hr_inicio`, `hr_fin`, `tema`, `observaciones`, `ofrendas`, `cdp_id`, `enviado_por_lider_id`). Genera `UUID()` e invalida caché de dashboard. |
| 2 | **Script de Poblado y Test Data** | ✅ Implementado | `insert_test_data.py` automatiza la inserción idempotente de usuarios (`admin`, `supervisor`, `lider_cdp`), redes, Casas de Paz, líderes y reportes históricos de 8 semanas con hashes Werkzeug y UUIDs válidos. |
| 3 | **Dashboard con datos reales** | ✅ Cumplido | `dashboard_service.py` y `db_queries.py` implementan consultas reales, métricas por nivel (General, Red, CDP), filtros jerárquicos, modo mock, sistema de caché y estados vacíos. |
| 4 | **Filtros de reportes** | ✅ Implementado | `templates/reportes_admin.html`, `services/report_service.py` y `db_queries.get_reportes()` procesan búsqueda por texto (`q`), red (`red_id`), Casa de Paz (`cdp_id`) y rango de fechas (`fecha_desde`, `fecha_hasta`) tanto en base de datos como en modo mock. |
| 5 | **Paginación real conectada** | ✅ Implementado | Paginación server-side dinámica (`page`, `per_page`, `pages`, `total`) conectada en **Reportes**, **Usuarios** y **Líderes** (`services/report_service.py`, `services/user_service.py`, `services/leader_service.py`). |
| 6 | **Vistas de supervisor aisladas** | ✅ Implementado | Dashboard, Estructura, Reportes y Directorio de Líderes cuentan con aislamiento automático por red del supervisor logueado (`supervisor_red_id`). |
| 7 | **CRUD de Usuarios (Mutaciones POST)** | ⚠️ Parcial | **Lectura, filtros y paginación completados** (`get_usuarios_context`). Pendiente conectar el procesamiento `POST` en formularios de crear/editar y alternar estado activo/inactivo (`is_active`). |
| 8 | **CRUD de Casas de Paz (Mutaciones POST)** | ⚠️ Parcial | Visualización en estructura y asignación de líderes/usuarios funcional. Pendiente conectar operaciones `POST` (`INSERT`/`UPDATE`/`DELETE`/pausar) en formularios admin. |
| 9 | **CRUD de Redes (Mutaciones POST)** | ⚠️ Parcial | Visualización jerárquica y filtros de red completados. Pendiente conectar formularios de creación/edición de redes y asignación de supervisor vía `POST`. |
| 10 | **CRUD de Líderes (Mutaciones POST)** | ⚠️ Parcial | **Lectura, filtros por red/CDP y paginación completados** (`get_lideres_context`). Pendiente conectar el guardado de nuevos líderes y edición vía formulario `POST`. |
| 11 | **Vista de reportes enviados para CDP** | ⚠️ Parcial | `cdp/dashboard` (`index.html`) cuenta con maquetación y acceso al formulario de reporte; falta dinamizar el historial semanal y resumen de métricas del líder en sesión. |
| 12 | **Módulo de Perfil y Cambio de Contraseña** | ⚠️ Parcial | `cdp_service.get_perfil_data()` y `update_perfil()` implementados. Falta formulario específico para cambio seguro de contraseña con verificación de clave actual. |
| 13 | **Flash messages y toasts** | ❌ Pendiente | Falta integrar contenedor visual de `get_flashed_messages()` en `admin_layout.html` y emitir mensajes tras operaciones CRUD. |
| 14 | **Exportar PDF/Excel** | ❌ Pendiente | Botones visuales maquetados; falta implementar librerías de generación (e.g. ReportLab / openpyxl) y endpoints de descarga con filtros aplicados. |
| 15 | **Búsqueda en tiempo real (Client-side)** | ⚠️ Parcial | Filtros por GET implementados en Reportes, Usuarios, Líderes y Dashboard; en Estructura el filtrado por chips de red es dinámico en frontend. Falta búsqueda instantánea sin recarga vía JavaScript en tablas admin. |
| 16 | **Contactar por WhatsApp** | ⚠️ Parcial | Enlaces `wa.me` generados con teléfonos de líderes y CDPs. Pendiente normalización de código de país internacional (`+58`, `+52`, etc.). |

---

### Funcionalidades ya cumplidas o disponibles

- **Autenticación y Seguridad de Acceso**:
  - Login con validación y hasheo seguro mediante Werkzeug (`scrypt`/`pbkdf2`), con migración transparente de contraseñas legacy.
  - Decorador `@role_required` para control de acceso estricto por roles (`admin`, `supervisor`, `lider_cdp`).
  - Protección de endpoints contra manipulación de identificadores y aislamiento de supervisores.
- **Conectividad, Resiliencia y Datos de Prueba**:
  - Conexión centralizada con `database.py`, circuit breaker con reintentos automáticos y fallback transparente a `mock_data.py`.
  - Script automatizado `insert_test_data.py` compatible con el esquema MySQL actual, capaz de poblar usuarios, redes, CDPs, líderes y 18 reportes históricos de 8 semanas.
- **Módulo de Reportes (Admin & Supervisor)**:
  - Consultas SQL completas con cálculo de asistencia total, filtros combinados (búsqueda de texto, red, CDP, fechas) y paginación server-side.
  - Modal de detalle/visualización estructurado y diseño adaptativo.
- **Directorios Administrativos (Usuarios y Líderes)**:
  - Servicios desacoplados `user_service.py` y `leader_service.py` con paginación server-side y filtros funcionales sobre base de datos.
- **Módulo de Estructura**:
  - Vista jerárquica de redes y CDPs con filtrado interactivo por chips, avatares representativos, eliminación de doble scrollbar y cumplimiento de contraste accesible WCAG 2.2 AA/AAA.
- **Dashboard Multi-Nivel**:
  - KPIs globales, ranking de redes con cumplimiento semanal, distribución de asistencia, tendencias mensuales y alertas de casas sin reporte (14+ días).

---

### Inconsistencias técnicas y pendientes inmediatos

1. **Mutaciones POST en CRUDs Admin**: Conectar las rutas de creación y edición (Usuarios, Redes, Casas de Paz, Líderes) con validación de datos en backend y persistencia en BD.
2. **Protección CSRF**: Incorporar tokens CSRF en todos los formularios HTML antes de habilitar mutaciones `POST`.
3. **Módulo de Perfil (Contraseña)**: Implementar endpoint y modal para que el usuario pueda cambiar su contraseña verificando la actual.
4. **Historial Dinámico en Home CDP**: Conectar las métricas y reportes recientes en la vista de Casa de Paz (`index.html`) con la sesión del líder.
5. **Flash Messages & Toasts**: Añadir componente Toast / Alert en `admin_layout.html` para notificar éxito/error tras mutaciones.
6. **Exportación de Reportes**: Crear endpoints para descarga de reportes en PDF y Excel con filtros aplicados.

---

## 2. Problemas de seguridad

| # | Problema | Estado / severidad | Detalle |
|---|---|---|---|
| 1 | **Contraseñas en texto plano** | ✅ Resuelto | Login y scripts de datos usan hashes Werkzeug seguros. Los nuevos endpoints CRUD deben aplicar `generate_password_hash()`. |
| 2 | **Sin protección CSRF** | 🔴 Alta / Pendiente | Los formularios POST no incluyen tokens CSRF. Implementar protección (Flask-WTF o token de sesión) al activar los CRUDs. |
| 3 | **Credenciales de BD por defecto** | 🟡 Media / Pendiente | `config.py` y `insert_test_data.py` permiten variables de entorno (`.env`), pero mantienen fallbacks para desarrollo local. |
| 4 | **Manejo de conexiones** | ✅ Bueno | Servicios principales (`cdp_service`, `report_service`, `dashboard_service`, `user_service`, `leader_service`) usan `try/finally` asegurando el cierre de conexiones. |
| 5 | **Debug habilitado por defecto** | 🟡 Media / Pendiente | `DEBUG=True` activo en desarrollo. Desactivar en configuración de producción. |
| 6 | **Modo demo permisivo** | 🟡 Media / Pendiente | Fallback mock activo solo cuando la BD no está disponible. |
| 7 | **Validación de entrada en CRUDs** | 🟡 Media / Pendiente | Requerido validar tipos, rangos numéricos, unicidad de nombres/códigos y relaciones FK al habilitar mutaciones `POST`. |

---

## 3. Mejoras UI/UX

| # | Mejora | Estado actual | Detalle / Trabajo pendiente |
|---|---|---|---|
| 1 | **Home CDP** | ⚠️ Parcial | Maquetada; falta enlazar historial de reportes y equipo de líderes del usuario autenticado. |
| 2 | **Responsive en móviles y tablets** | ✅ Avanzado | Tablas con visualización tipo tarjeta en mobile, chips horizontales con scroll táctil, header desktop adaptativo y breakpoints limpios. |
| 3 | **Accesibilidad y Contraste de Color** | ✅ Implementado | Colores ajustados bajo estándar WCAG 2.2 AA/AAA en `estructura.css`, selectores de foco visibles (`:focus-visible`) e insignias con alto contraste. |
| 4 | **Doble scrollbar** | ✅ Resuelto | Eliminado el scroll interno anidado en `.casas-section` y `.estructura-main`, dejando exclusivamente la barra global. |
| 5 | **Sidebar visual limpio** | ✅ Implementado | Scroll lateral estilizado y limpio en `sidebar.css` preservando navegación fluida. |
| 6 | **Estados vacíos** | ✅ Implementado | Implementados en Dashboard, Estructura, Reportes, Usuarios y Líderes (`.empty-state`). |
| 7 | **Feedback de botones copiar** | ❌ Pendiente | Implementar Clipboard API con feedback visual al copiar credenciales de usuarios. |
| 8 | **Tooltips del gráfico donut** | ⚠️ Parcial | Leyenda funcional; falta tooltip flotante en los segmentos SVG/Canvas. |
| 9 | **Mensajes de operación (Toasts)** | ❌ Pendiente | Renderizar `get_flashed_messages()` en `admin_layout.html`. |
| 10 | **Consistencia de enlaces y botones** | ⚠️ Parcial | Conectar enlaces contextuales de estructura y acciones de edición en usuarios/líderes a rutas POST funcionales. |

---

## 4. Estructura de Base de Datos Actual y Verificada (`serv_comunitario`)

Esquema SQL exacto y verificado en el entorno de ejecución:

```sql
-- --------------------------------------------------------
-- Tabla: usuario
-- --------------------------------------------------------
CREATE TABLE `usuario` (
  `id` char(36) NOT NULL DEFAULT uuid(),
  `username` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `tipo_usuario` enum('admin','supervisor','lider_cdp') NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Tabla: red
-- --------------------------------------------------------
CREATE TABLE `red` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `supervisor_id` char(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_red_supervisor` (`supervisor_id`),
  CONSTRAINT `fk_red_supervisor` FOREIGN KEY (`supervisor_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Tabla: cdp (Casa de Paz)
-- --------------------------------------------------------
CREATE TABLE `cdp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `anfitrion` varchar(30) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `direccion` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `red_id` int(11) NOT NULL,
  `usuario_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  KEY `fk_cdp_red` (`red_id`),
  CONSTRAINT `fk_cdp_red` FOREIGN KEY (`red_id`) REFERENCES `red` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_cdp_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Tabla: lider
-- --------------------------------------------------------
CREATE TABLE `lider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  `rol` enum('Lider','Sublider') NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `cdp_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_lider_cdp` (`cdp_id`),
  CONSTRAINT `fk_lider_cdp` FOREIGN KEY (`cdp_id`) REFERENCES `cdp` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Tabla: reporte
-- --------------------------------------------------------
CREATE TABLE `reporte` (
  `id` char(36) NOT NULL DEFAULT uuid(),
  `nro_niños` int(11) NOT NULL DEFAULT 0,
  `nro_regulares` int(11) NOT NULL DEFAULT 0,
  `nro_visitas` int(11) NOT NULL DEFAULT 0,
  `nro_comprometidos` int(11) NOT NULL DEFAULT 0,
  `reconciliaciones` int(11) NOT NULL DEFAULT 0,
  `confesiones` int(11) NOT NULL DEFAULT 0,
  `cesta_amor` tinyint(1) DEFAULT 0,
  `fecha` date DEFAULT curdate(),
  `hr_inicio` time NOT NULL,
  `hr_fin` time NOT NULL,
  `tema` varchar(100) NOT NULL,
  `observaciones` text DEFAULT NULL,
  `ofrendas` decimal(10,2) NOT NULL DEFAULT 0.00,
  `ofrendas_usd` decimal(10,2) NOT NULL DEFAULT 0.00,
  `ofrendas_bs` decimal(10,2) NOT NULL DEFAULT 0.00,
  `cdp_id` int(11) NOT NULL,
  `enviado_por_lider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_reporte_cdp` (`cdp_id`),
  KEY `fk_reporte_lider` (`enviado_por_lider_id`),
  CONSTRAINT `fk_reporte_cdp` FOREIGN KEY (`cdp_id`) REFERENCES `cdp` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reporte_lider` FOREIGN KEY (`enviado_por_lider_id`) REFERENCES `lider` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

---

## 5. Priorización por Fases Actualizada

### Fase 1 — Núcleo, Reportes y Datos (✅ Completada)
- [x] Conexión centralizada a base de datos con circuit breaker y fallbacks transparentes.
- [x] Corrección e inserción de reportes (`cdp_service.py` y `db_queries.insertar_reporte` alineados con el esquema SQL).
- [x] Script automatizado `insert_test_data.py` con datos de prueba realistas, hashes Werkzeug y compatibilidad con el esquema.
- [x] Módulo de reportes dinámico para Admin y Supervisor con filtros multidimensionales (texto, red, casa, fechas) y paginación server-side.
- [x] Dashboard multi-nivel conectado a datos reales, filtros jerárquicos y caché.
- [x] Directorios de lectura de Usuarios y Líderes con filtros y paginación conectada a BD.
- [x] Depuración responsive, solución de doble scrollbar y accesibilidad WCAG 2.2 AA/AAA en estructura y reportes.

### Fase 2 — Mutaciones CRUDs Administrativos (Próximo paso prioritario)
- [ ] **CRUD Usuarios (POST)**: Formulario crear/editar, activar/desactivar (`is_active`) y hasheo seguro de contraseñas.
- [ ] **CRUD Casas de Paz (POST)**: Crear, editar, pausar/activar, asignar usuario y vincular a red.
- [ ] **CRUD Redes (POST)**: Crear, editar, pausar/activar, asignar supervisor y gestionar casas asociadas.
- [ ] **CRUD Líderes (POST)**: Crear, editar, eliminar/desactivar y vincular a Casas de Paz.
- [ ] Incorporación de validación de formularios backend y protección CSRF.

### Fase 3 — Home CDP, Perfil y Notificaciones
- [ ] Historial y resumen dinámico en el panel de Casa de Paz (`index.html`) según líder en sesión.
- [ ] Módulo de Perfil: Cambio de contraseña con verificación de clave actual.
- [ ] Sistema de Flash Messages / Toasts globales en `admin_layout.html` para retroalimentación de operaciones.

### Fase 4 — Exportación y Polish final
- [ ] Exportación de reportes y listados a PDF y Excel con filtros aplicados.
- [ ] Búsqueda en tiempo real sin recarga en tablas de Usuarios y Líderes.
- [ ] Tooltips interactivos y accesibles en gráficos del dashboard.
- [ ] Configuración segura de producción (variables de entorno obligatorias, `DEBUG=False`, desactivación de modo mock).
