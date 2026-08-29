# Requerimientos — Proyecto Vino Nuevo

## Descripción General
Aplicación web de gestión y reportes para un servicio comunitario (ministerio "Vino Nuevo").  
**Stack:** Python Flask + MySQL (PyMySQL) + HTML/CSS (Jinja2)

---

## 1. Estado general de requerimientos

**Criterio:** Se considera implementado solo lo que está conectado a una ruta, servicio, consulta o listener funcional. El HTML estático por sí solo se considera maquetado.

| # | Requerimiento | Estado actual | Evidencia y trabajo pendiente |
|---|---|---|---|
| 1 | **INSERT de reportes en BD** | ✅ Implementado | `services/cdp_service.py` y `db_queries.insertar_reporte()` alineados con el esquema SQL. Genera `UUID()`, invalida caché de dashboard y soporta ofrendas duales (USD/Bs). |
| 2 | **Script de Poblado y Test Data** | ✅ Implementado | `insert_test_data.py` automatiza la inserción idempotente de usuarios, redes, Casas de Paz, líderes y reportes históricos de 8 semanas con hashes Werkzeug y UUIDs válidos. |
| 3 | **Dashboard con datos reales** | ✅ Cumplido | `dashboard_service.py` y `db_queries.py` con consultas reales, métricas por nivel, filtros jerárquicos, caché y estados vacíos. Nuevo diseño con tarjetas dinámicas y scripts dedicados (`dashboard.js`, `lider_dashboard.js`). |
| 4 | **Filtros de reportes** | ✅ Implementado | Búsqueda por texto, red, Casa de Paz y rango de fechas en admin y supervisor. Soporte de ofrendas duales (USD/Bs) en la vista y modales. |
| 5 | **Paginación real conectada** | ✅ Implementado | Paginación server-side con ventana deslizante (±2 páginas) y puntos suspensivos en **Reportes**, **Usuarios** y **Líderes**. |
| 6 | **Vistas de supervisor aisladas** | ✅ Implementado | Dashboard, Estructura, Reportes y Directorio de Líderes con aislamiento automático por red del supervisor logueado. |
| 7 | **CRUD de Usuarios (Mutaciones POST)** | ⚠️ Parcial | Lectura, filtros y paginación completados. Formulario crear/editar maquetado (`form_usuario.html`). Pendiente conectar procesamiento `POST` con validación backend y alternar `is_active`. |
| 8 | **CRUD de Casas de Paz (Mutaciones POST)** | ⚠️ Parcial | Visualización en estructura y asignación de líderes/usuarios funcional. Pendiente conectar operaciones `POST` en formularios admin. |
| 9 | **CRUD de Redes (Mutaciones POST)** | ⚠️ Parcial | Visualización jerárquica y filtros de red completados. Pendiente conectar formularios de creación/edición y asignación de supervisor vía `POST`. |
| 10 | **CRUD de Líderes (Mutaciones POST)** | ⚠️ Parcial | Lectura, filtros por red/CDP y paginación completados. Pendiente conectar guardado de nuevos líderes y edición vía formulario `POST`. |
| 11 | **Vista de reportes enviados para CDP** | ⚠️ Parcial | `index.html` con maquetación, modales de detalle/edición/eliminación y script `lider_dashboard.js` funcional. Falta conectar el formulario de envío de reporte con el servicio. |
| 12 | **Módulo de Perfil y Cambio de Contraseña** | ✅ Implementado | Página de perfil rediseñada con cambio de usuario, cambio de contraseña (verificación de clave actual, barra de fortaleza, indicador de coincidencia) y toggle de tema oscuro/claro. `cdp_service.py` provee `get_perfil_data()` y `update_perfil()`. |
| 13 | **Flash messages y toasts** | ✅ Implementado | `get_flashed_messages(with_categories=true)` integrado en `admin_layout.html` con toast auto-dismiss (5s), soporte de categorías (`success`, `danger`, `warning`, `info`) e iconos contextuales. |
| 14 | **Exportar PDF/Excel** | ❌ Pendiente | Botones visuales maquetados; falta implementar librerías de generación (e.g. ReportLab / openpyxl) y endpoints de descarga con filtros aplicados. |
| 15 | **Búsqueda en tiempo real (Client-side)** | ⚠️ Parcial | Filtros por GET con paginación de ventana en todas las vistas admin. Falta búsqueda instantánea sin recarga vía JavaScript en tablas. |
| 16 | **Contactar por WhatsApp** | ⚠️ Parcial | Enlaces `wa.me` generados con teléfonos de líderes y CDPs. Pendiente normalización de código de país internacional. |
| 17 | **Modo Oscuro** | ✅ Implementado | `dark_theme.css` con variable CSS `data-theme="dark"`, persistencia en `localStorage`, detección anti-FOUC y toggle desde perfil y login. |
| 18 | **Páginas de Error** | ✅ Implementado | 403 y 404 rediseñadas con diseño consistente, botón de retorno y look-and-feel unificado con la aplicación. |

---

### Funcionalidades ya cumplidas o disponibles

- **Autenticación y Seguridad de Acceso**:
  - Login rediseñado con validación y hasheo seguro mediante Werkzeug (`pbkdf2:sha256`), migración transparente de contraseñas legacy y toggle de modo oscuro.
  - Decorador `@role_required` para control de acceso estricto por roles (`admin`, `supervisor`, `lider_cdp`).
  - Protección de endpoints contra manipulación de identificadores y aislamiento de supervisores.
  - Flash messages con categorías para retroalimentación de errores de autenticación.
- **Conectividad, Resiliencia y Datos de Prueba**:
  - Conexión centralizada con `database.py`, circuit breaker con reintentos automáticos y fallback transparente a `mock_data.py`.
  - Script `insert_test_data.py` compatible con el esquema MySQL actual, capaz de poblar usuarios, redes, CDPs, líderes y reportes históricos.
- **Módulo de Reportes (Admin & Supervisor)**:
  - Consultas SQL completas con cálculo de asistencia total, filtros combinados y paginación server-side con ventana deslizante.
  - Modales de detalle/visualización, edición y eliminación con confirmación. Soporte de ofrendas duales USD/Bs.
- **Directorios Administrativos (Usuarios y Líderes)**:
  - Servicios desacoplados con paginación server-side, filtros funcionales y formularios CRUD maquetados.
- **Módulo de Estructura**:
  - Vista jerárquica de redes y CDPs con filtrado interactivo por chips, avatares representativos y accesibilidad WCAG 2.2 AA/AAA.
- **Dashboard Multi-Nivel**:
  - KPIs globales, ranking de redes, distribución de asistencia, tendencias mensuales y alertas de casas sin reporte. Nuevo diseño con tarjetas dinámicas y scripts dedicados.
- **Módulo de Perfil**:
  - Cambio de usuario, cambio de contraseña con verificación de clave actual, barra de fortaleza y toggle de tema oscuro/claro con persistencia.
- **Modo Oscuro**:
  - Tema global vía `data-theme` attribute, CSS con variables, persistencia en `localStorage`, anti-FOUC y toggle desde login y perfil.

---

### Inconsistencias técnicas y pendientes inmediatos

1. **Mutaciones POST en CRUDs Admin**: Conectar las rutas de creación y edición (Usuarios, Redes, Casas de Paz, Líderes) con validación de datos en backend y persistencia en BD.
2. **Protección CSRF**: Incorporar tokens CSRF en todos los formularios HTML antes de habilitar mutaciones `POST`.
3. **Rate Limiting en Login**: Implementar limitación de intentos de acceso para prevenir fuerza bruta.
4. **Headers de Seguridad**: Agregar `X-Frame-Options`, `Content-Security-Policy`, `HSTS` y `Referrer-Policy` en todas las respuestas.
5. **Hardening de Sesiones**: Configurar `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE` y `PERMANENT_SESSION_LIFETIME`.
6. **Exportación de Reportes**: Crear endpoints para descarga de reportes en PDF y Excel con filtros aplicados.
7. **Protección de API**: Agregar `@login_required` al endpoint `/api/dashboard/datos` que actualmente es público.
8. **Validación de Entrada Server-Side**: Implementar validación de tipos, longitudes, formatos y unicidad en todos los formularios.

---

## 2. Problemas de seguridad

### 2.1 Estado actual de controles de seguridad

| # | Área de Seguridad | Estado | Severidad |
|---|---|---|---|
| 1 | **Protección CSRF** | 🔴 **CRÍTICO / Pendiente** | Ningún formulario incluye tokens CSRF. Todos los POST son vulnerables a ataques CSRF. |
| 2 | **Rate Limiting en Login** | 🔴 **CRÍTICO / Pendiente** | Sin limitación de intentos. Ataques de fuerza bruta ilimitados contra todas las cuentas. |
| 3 | **Validación de Entrada** | 🟠 **ALTA / Pendiente** | Sin librería de validación server-side (marshmallow, WTForms). Sin sanitización XSS (bleach, markupsafe). Solo `.strip()` y casting `int()` básico. |
| 4 | **Headers de Seguridad** | 🟠 **ALTA / Pendiente** | Solo `X-Content-Type-Options: nosniff` en archivos estáticos. Faltan: `X-Frame-Options`, `Content-Security-Policy`, `HSTS`, `Referrer-Policy`, `Permissions-Policy`. |
| 5 | **Configuración de Sesiones** | 🟠 **ALTA / Parcial** | `SECRET_KEY` configurada pero sin hardening de cookies (`Secure`, `HttpOnly`, `SameSite`). Sin `PERMANENT_SESSION_LIFETIME`. |
| 6 | **Autenticación en API** | 🟠 **ALTA / Pendiente** | Endpoint `/api/dashboard/datos` sin `@login_required`. Datos de dashboard accesibles sin autenticación. |
| 7 | **Fortaleza de Contraseñas** | 🟡 **MEDIA / Débil** | Solo mínimo 6 caracteres. Sin requisitos de mayúsculas, números o símbolos. Sin máximo de longitud. |
| 8 | **Logout** | 🟡 **MEDIA / Parcial** | Usa `session.pop()` parcial en vez de `session.clear()`. Sin invalidación server-side de sesión. Sin regeneración de sesión post-login. |
| 9 | **Credenciales por Defecto** | 🟡 **MEDIA / Pendiente** | Fallbacks de BD en `config.py` para desarrollo. `.env` con `SECRET_KEY` en el repositorio. |
| 10 | **Debug en Producción** | 🟡 **MEDIA / Pendiente** | `DEBUG=True` en desarrollo. Asegurar `DEBUG=False` en producción. |
| 11 | **Contraseñas en Texto Plano** | ✅ **Resuelto** | Login y scripts usan hashes Werkzeug seguros (`pbkdf2:sha256`). Migración automática de legado. |
| 12 | **SQL Injection** | ✅ **Protegido** | Todas las consultas usan parámetros `%s` con tuplas. Sin interpolación de datos de usuario en SQL. |
| 13 | **Manejo de Conexiones** | ✅ **Bueno** | Servicios principales usan `try/finally` para cierre seguro de conexiones. |
| 14 | **Flash Messages** | ✅ **Implementado** | Toasts con categorías, auto-dismiss e iconos contextuales en `admin_layout.html`. |
| 15 | **Control de Acceso por Roles** | ✅ **Implementado** | `@login_required` y `@role_required` en todas las rutas protegidas (admin, supervisor, líder). Aislamiento de supervisores por red. |

### 2.2 Acciones correctivas prioritarias

| Prioridad | Acción | Dependencias |
|---|---|---|
| **P0** | Instalar `flask-wtf` y habilitar `CSRFProtect(app)`. Agregar `{{ csrf_token() }}` a todos los formularios. | Ninguna |
| **P0** | Instalar `flask-limiter` y aplicar rate limiting al login (ej. 5 intentos/min por IP). | Ninguna |
| **P1** | Agregar `@login_required` a `routes/api_routes.py` para proteger `/api/dashboard/datos`. | Ninguna |
| **P1** | Instalar `flask-talisman` o configurar headers de seguridad en `after_request` para todas las respuestas (CSP, HSTS, X-Frame-Options, Referrer-Policy). | Ninguna |
| **P1** | Configurar cookies de sesión seguras: `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`, `PERMANENT_SESSION_LIFETIME=timedelta(hours=2)`. | Ninguna |
| **P1** | Eliminar `.env` del repositorio (agregar a `.gitignore`) y rotar el `SECRET_KEY` actual. | Ninguna |
| **P2** | Implementar validación server-side de entrada (longitudes, tipos, formatos de teléfono, unicidad de username). | Elegir librería (WTForms / marshmallow) |
| **P2** | Endurecer política de contraseñas: mínimo 8 caracteres, al menos 1 mayúscula, 1 número, 1 símbolo. Máximo 128 caracteres. | Instalar librería o validar manualmente |
| **P2** | Usar `session.clear()` en logout y considerar sesiones server-side para invalidación real. | Evaluar Flask-Session |
| **P3** | Implementar sanitización XSS con `bleach` o `markupsafe.escape()` en campos de texto libre (tema, observaciones, nombre). | Instalar librería |

---

## 3. Mejoras UI/UX

| # | Mejora | Estado actual | Detalle / Trabajo pendiente |
|---|---|---|---|
| 1 | **Home CDP** | ⚠️ Parcial | Maquetada con modales de reporte (detalle, editar, eliminar) y script `lider_dashboard.js`. Falta conectar el formulario de envío de reporte con el servicio. |
| 2 | **Responsive en móviles y tablets** | ✅ Avanzado | Tablas tipo tarjeta en mobile, chips horizontales con scroll táctil, header desktop adaptativo con 2 breakpoints (≤1100px, ≤745px). |
| 3 | **Accesibilidad y Contraste de Color** | ✅ Implementado | WCAG 2.2 AA/AAA en `estructura.css`, selectores de foco visibles, insignias con alto contraste. |
| 4 | **Doble scrollbar** | ✅ Resuelto | Eliminado el scroll interno anidado en vistas admin. |
| 5 | **Sidebar visual limpio** | ✅ Implementado | Scroll lateral estilizado en `sidebar.css` preservando navegación fluida. |
| 6 | **Estados vacíos** | ✅ Implementado | Implementados en Dashboard, Estructura, Reportes, Usuarios y Líderes. |
| 7 | **Feedback de botones copiar** | ❌ Pendiente | Implementar Clipboard API con feedback visual al copiar credenciales de usuarios. |
| 8 | **Tooltips del gráfico donut** | ⚠️ Parcial | Leyenda funcional; falta tooltip flotante en los segmentos SVG/Canvas. |
| 9 | **Mensajes de operación (Toasts)** | ✅ Implementado | Toasts auto-dismiss con categorías (`success`, `danger`, `warning`, `info`) integrados en `admin_layout.html`. |
| 10 | **Consistencia de enlaces y botones** | ⚠️ Parcial | Conectar enlaces contextuales de estructura y acciones de edición a rutas POST funcionales. |
| 11 | **Modo Oscuro** | ✅ Implementado | Toggle global desde login y perfil. Persistencia en `localStorage`. Anti-FOUC. |
| 12 | **Diseño de Login** | ✅ Implementado | Login rediseñado con tarjeta centrada, iconos, toggle contraseña, banner de entorno de desarrollo y modo oscuro. |
| 13 | **Páginas de Error** | ✅ Implementado | 403 y 404 con diseño consistente, iconos y botón de retorno. |
| 14 | **Paginación con Ventana** | ✅ Implementado | Ventana deslizante ±2 páginas con puntos suspensivos en Reportes, Usuarios y Líderes. |

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
- [x] Corrección e inserción de reportes con soporte de ofrendas duales USD/Bs.
- [x] Script automatizado `insert_test_data.py` con datos de prueba realistas.
- [x] Módulo de reportes dinámico con filtros multidimensionales y paginación server-side con ventana.
- [x] Dashboard multi-nivel conectado a datos reales, filtros jerárquicos y caché.
- [x] Directorios de lectura de Usuarios y Líderes con filtros y paginación.
- [x] Depuración responsive, solución de doble scrollbar y accesibilidad WCAG 2.2 AA/AAA.

### Fase 2 — UI/UX, Perfil y Tema Oscuro (✅ Completada)
- [x] Login rediseñado con tarjeta centrada, toggle contraseña y modo oscuro.
- [x] Perfil completo: cambio de usuario, cambio de contraseña con verificación y barra de fortaleza.
- [x] Modo oscuro global con persistencia en `localStorage` y anti-FOUC.
- [x] Dashboard rediseñado con tarjetas dinámicas y scripts dedicados.
- [x] Paginación con ventana deslizante en Reportes, Usuarios y Líderes.
- [x] Flash messages / toasts con categorías y auto-dismiss.
- [x] Páginas de error 403 y 404 con diseño consistente.

### Fase 3 — Seguridad y Hardening (Próximo paso prioritario)
- [ ] **CSRF**: Instalar `flask-wtf`, habilitar `CSRFProtect(app)` y agregar tokens a todos los formularios.
- [ ] **Rate Limiting**: Instalar `flask-limiter`, limitar login a 5 intentos/min por IP.
- [ ] **Headers de Seguridad**: Configurar CSP, HSTS, X-Frame-Options, Referrer-Policy en `after_request`.
- [ ] **Hardening de Sesiones**: Cookies seguras (`Secure`, `HttpOnly`, `SameSite='Lax'`), timeout de 2 horas.
- [ ] **Protección de API**: Agregar `@login_required` a `/api/dashboard/datos`.
- [ ] **Eliminar `.env` del repo**: Agregar a `.gitignore` y rotar `SECRET_KEY`.

### Fase 4 — Mutaciones CRUDs Administrativos
- [ ] **CRUD Usuarios (POST)**: Conectar formularios con validación backend, hasheo de contraseñas y alternar `is_active`.
- [ ] **CRUD Casas de Paz (POST)**: Crear, editar, pausar/activar, asignar usuario y vincular a red.
- [ ] **CRUD Redes (POST)**: Crear, editar, pausar/activar, asignar supervisor.
- [ ] **CRUD Líderes (POST)**: Crear, editar, eliminar/desactivar y vincular a Casas de Paz.
- [ ] **Validación Server-Side**: Implementar validación de tipos, longitudes, formatos y unicidad.

### Fase 5 — Exportación y Polish final
- [ ] Exportación de reportes y listados a PDF y Excel con filtros aplicados.
- [ ] Búsqueda en tiempo real sin recarga en tablas de Usuarios y Líderes.
- [ ] Tooltips interactivos y accesibles en gráficos del dashboard.
- [ ] Configuración segura de producción (`DEBUG=False`, variables de entorno obligatorias, desactivación de mock).
