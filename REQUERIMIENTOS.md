# Requerimientos — Proyecto Vino Nuevo

## Descripción General
Aplicación web de gestión y reportes para un servicio comunitario (ministerio "Vino Nuevo").  
**Stack:** Python Flask + MySQL (PyMySQL) + HTML/CSS (Jinja2)

---

## 1. Estado general de requerimientos

**Criterio:** se considera implementado solo lo que está conectado a una ruta, servicio, consulta o listener funcional. El HTML estático por sí solo se considera maquetado.

| # | Requerimiento | Estado actual | Evidencia y trabajo pendiente |
|---|---|---|---|
| 1 | **INSERT de reportes en BD** | ✅ Implementado | `services/cdp_service.py` y `db_queries.insertar_reporte()` ya están alineados con el esquema SQL (`nro_niños`, `nro_regulares`, `nro_visitas`, `nro_comprometidos`, `reconciliaciones`, `confesiones`, `cesta_amor`, `hr_inicio`, `hr_fin`, `tema`, `observaciones`, `ofrendas`, `cdp_id`, `enviado_por_lider_id`). Genera `UUID()` e invalida caché de dashboard. |
| 2 | **CRUD de Usuarios** | ❌ Pendiente | `routes/admin_routes.py` solo renderiza plantillas. `usuarios_admin.html` y `form_usuario.html` contienen datos demo y botones sin procesamiento POST a base de datos. |
| 3 | **CRUD de Casas de Paz** | ❌ Pendiente | Las rutas de creación, edición y eliminación de CDP no ejecutan operaciones `INSERT`/`UPDATE`/`DELETE` en BD. |
| 4 | **CRUD de Redes** | ❌ Pendiente | `red/editar` solo muestra el formulario; las acciones del menú contextual de estructura requieren conectar rutas y lógica de persistencia. |
| 5 | **CRUD de Líderes** | ❌ Pendiente | `lider_admin.html` muestra datos maquetados y `lider/editar` no procesa formularios a BD. |
| 6 | **Dashboard con datos reales** | ✅ Cumplido | `dashboard_service.py` y `db_queries.py` implementan consultas reales, métricas por nivel (General, Red, CDP), filtros jerárquicos, modo mock, sistema de caché y estados vacíos. |
| 7 | **Vista de reportes enviados para CDP** | ⚠️ Parcial | `cdp/dashboard` (`index.html`) tiene el diseño y acceso al formulario de reporte; falta conectar el historial y métricas dinámicas del líder logueado. |
| 8 | **Filtros de reportes** | ✅ Implementado | `templates/reportes_admin.html`, `services/report_service.py` y `db_queries.get_reportes()` procesan búsqueda por texto (`q`), red (`red_id`), Casa de Paz (`cdp_id`) y rango de fechas (`fecha_desde`, `fecha_hasta`) tanto en base de datos como en modo mock. |
| 9 | **Paginación real** | ⚠️ Parcial | **Reportes** ya cuenta con paginación server-side dinámica (`page`, `per_page`, cálculo de `total_paginas`). Falta implementar paginación conectada en **Usuarios** y **Líderes**. |
| 10 | **Exportar PDF/Excel** | ❌ Pendiente | Botones visuales maquetados; falta implementar librerías de generación (e.g. ReportLab / openpyxl) y endpoints de descarga. |
| 11 | **Búsqueda en tiempo real** | ⚠️ Parcial | Filtros por GET implementados en Reportes y Dashboard; en Estructura el filtrado por chips de red es dinámico en frontend. Falta filtrado en tiempo real sin recarga para tablas de Usuarios y Líderes. |
| 12 | **Flash messages y toasts** | ❌ Pendiente | Falta integrar contenedor visual de `get_flashed_messages()` en `admin_layout.html` y emitir mensajes tras operaciones CRUD. |
| 13 | **Contactar por WhatsApp** | ⚠️ Parcial | El dashboard genera enlaces `wa.me` con el teléfono del líder. Falta normalización de código de país y soporte en listados de líderes. |
| 14 | **Gestión de contraseña** | ❌ Pendiente | Login usa hashes seguros (Werkzeug scrypt); falta formulario en Perfil para que los usuarios cambien su clave verificando la actual. |
| 15 | **Vistas de supervisor** | ⚠️ Avanzado | Dashboard, Estructura y Reportes cuentan con rutas dedicadas, autorización de rol y aislamiento automático por red (`supervisor_red_id`). Falta dinamizar la vista de Líderes del supervisor. |

### Funcionalidades ya cumplidas o disponibles

- **Autenticación y Seguridad básica**: Login con validación de hashes Werkzeug, migración automática de contraseñas legacy, decoradores de sesión, verificación de roles (`admin`, `supervisor`, `cdp`) y protección contra manipulación de UUID en URL.
- **Conectividad y Resiliencia**: Conexión centralizada a MySQL con `database.py`, circuit breaker, fallback transparente a `mock_data.py` cuando no hay BD activa y liberación de conexiones con `finally`.
- **Módulo de Reportes (Admin & Supervisor)**: Consultas completas de reportes, formulario de filtros multidimensional (texto, red, casa, fechas), paginación real, modal de detalle/edición estructurado y vista responsive adaptada con botones de acción alineados.
- **Módulo de Estructura**: Visualización jerárquica de redes y casas de paz, filtrado interactivo por chips, avatares representativos de casas (`home`), eliminación de doble scrollbar (scroll global único), resolución de bugs de visibilidad en tablet/móvil y contraste de colores bajo pautas WCAG 2.2 AA/AAA.
- **Dashboard Multi-Nivel**: Métricas consolidadas, filtros dinámicos, ranking de casas, alertas de asistencia/ofrendas y caché en memoria.
- **Navegación e Identidad Visual**: Menú lateral responsive (`sidebar.css`) sin scrollbars invasivas, encabezado unificado `#admin-desktop-header`, header móvil y barra de navegación inferior móvil.

### Inconsistencias técnicas y pendientes inmediatos

1. **CRUDs Admin**: Conectar formularios de creación y edición (Usuarios, Redes, Casas de Paz, Líderes) con rutas `POST`, validación de datos y operaciones en base de datos.
2. **Protección CSRF**: Incorporar tokens CSRF en todos los formularios HTML antes de habilitar mutaciones `POST`.
3. **Módulo de Perfil**: Agregar endpoints y formularios para actualizar datos personales y cambiar contraseñas con hash.
4. **Exportación de Reportes**: Crear generadores de archivos PDF y Excel con filtros aplicados.
5. **Historial en Home CDP**: Conectar las métricas y reportes recientes en la vista de Casa de Paz (`index.html`).
6. **Flash Messages**: Añadir componente Toast / Alert en el layout principal para retroalimentar al usuario en cada acción.

---

## 2. Problemas de seguridad

| # | Problema | Estado / severidad | Detalle |
|---|---|---|---|
| 1 | **Contraseñas en texto plano** | ✅ Resuelto en Login | El login valida hashes Werkzeug y migra registros legacy. Garantizar que el alta de usuarios en el CRUD siempre aplique `generate_password_hash()`. |
| 2 | **Sin protección CSRF** | 🔴 Alta / Pendiente | Los formularios POST no incluyen tokens CSRF. Implementar protección (Flask-WTF o token de sesión) al activar los CRUDs. |
| 3 | **Credenciales de BD por defecto** | 🟡 Media / Pendiente | `config.py` permite usuario `root` y contraseña vacía por defecto. En producción deben ser obligatorias las variables de entorno (`.env`). |
| 4 | **Manejo de conexiones** | ✅ Bueno | Servicios principales (`cdp_service`, `report_service`, `dashboard_service`) usan `try/finally` para asegurar el cierre de conexiones. |
| 5 | **Debug habilitado por defecto** | 🟡 Media / Pendiente | `DEBUG` y desarrollo están activos por defecto en `run.py`/`config.py`. Desactivar en entorno de producción. |
| 6 | **Modo demo permisivo** | 🟡 Media / Pendiente | Modo mock habilitado para desarrollo sin BD. Debe quedar inhabilitado en producción. |
| 7 | **API sin autorización explícita** | 🟡 Media / Pendiente | Validar sesión, rol y aislamiento de supervisor en `/api/dashboard/datos`. |
| 8 | **Ausencia de validación de entrada** | 🟡 Media / Pendiente | Validar tipos, rangos numéricos, fechas y relaciones antes de ejecutar `INSERT`/`UPDATE` en los nuevos CRUDs. |

---

## 3. Mejoras UI/UX

| # | Mejora | Estado actual | Detalle / Trabajo pendiente |
|---|---|---|---|
| 1 | **Home CDP** | ⚠️ Parcial | Maquetada; falta enlazar historial de reportes y equipo de líderes reales. |
| 2 | **Responsive en móviles y tablets** | ✅ Avanzado | Tablas con visualización tipo tarjeta en mobile, chips horizontales con scroll táctil, header desktop oculto limpiamente vía `#admin-desktop-header` y corrección de bugs de visualización en resoluciones intermedias (769px–1024px). |
| 3 | **Accesibilidad y Contraste de Color** | ✅ Implementado en Estructura | Colores ajustados bajo estándar WCAG 2.2 AA/AAA en `estructura.css`, selectores de foco visibles (`:focus-visible`) e insignias con alto contraste. |
| 4 | **Doble scrollbar** | ✅ Resuelto en Estructura | Eliminado el scroll interno anidado en `.casas-section` y `.estructura-main`, dejando exclusivamente la barra de desplazamiento global de la página. |
| 5 | **Sidebar visual limpio** | ✅ Implementado | Eliminadas las barras de desplazamiento grisáceas del menú lateral en `sidebar.css` preservando la funcionalidad de scroll táctil en dispositivos compactos. |
| 6 | **Estados vacíos** | ✅ Parcial | Implementados en Dashboard, Estructura y Reportes (`.empty-state`). Pendiente agregar en Usuarios y Líderes. |
| 7 | **Feedback de botones copiar** | ❌ Pendiente | Implementar Clipboard API con feedback visual al copiar credenciales de usuarios. |
| 8 | **Tooltips del gráfico donut** | ⚠️ Parcial | Leyenda funcional; falta tooltip flotante en los segmentos SVG/Canvas. |
| 9 | **Mensajes de operación (Toasts)** | ❌ Pendiente | Renderizar `get_flashed_messages()` en `admin_layout.html`. |
| 10 | **Consistencia de enlaces y botones** | ⚠️ Parcial | Enlaces de reportes y dashboard conectados; conectar enlaces `#` en menú contextual de redes y acciones de líderes/usuarios. |

---

## 4. Estructura de Base de Datos Requerida

Basado en los formularios, se necesitan estas tablas en `serv_comunitario`:

```sql
CREATE TABLE `cdp` (
  `id` int(11) NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `anfitrion` varchar(30) NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `direccion` varchar(100) NOT NULL,
  `red_id` int(11) NOT NULL,
  `usuario_id` char(36) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lider`
--

CREATE TABLE `lider` (
  `id` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  `rol` enum('Lider','Sublider') NOT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `cdp_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `red`
--

CREATE TABLE `red` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `supervisor_id` char(36) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `red`
--

INSERT INTO `red` (`id`, `nombre`, `supervisor_id`) VALUES
(1, 'Cielos Abiertos', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reporte`
--

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
  `cdp_id` int(11) NOT NULL,
  `enviado_por_lider_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` char(36) NOT NULL DEFAULT uuid(),
  `username` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `tipo_usuario` enum('admin','supervisor','cdp') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `nombre` varchar(30) DEFAULT NULL,
  `apellido` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `username`, `password`, `tipo_usuario`, `is_active`, `nombre`, `apellido`) VALUES
('1d4f7c99-7d51-11f1-bf9e-2016d8516279', 'lider', 'scrypt:32768:8:1$tmeJa8FoOIXrVNBa$d6233d2695ddf1452fd4afbce1b459ba56e2d4c05307a239fe1987a5dce6f62e4f9f54415755f0ce9df853859b9b695b449a045b025f8a9454a00151c326c175', 'cdp', 1, 'Mauricio', 'Leal'),
('702f2129-7d4e-11f1-bf9e-2016d8516279', 'admin', 'scrypt:32768:8:1$M2qNh7uNiBJLSNrh$f90e51fc287f96a402bc301fbda8c6be26ab4ccc40a9daef55334779a0df71bc656bd5344e35d19f70de175e3f6956227c003f21298d69a83daf03f98fee2f6e', 'admin', 1, 'Mauricio', 'Leal'),
('ca58cfc6-8337-11f1-8217-2016d8516279', 'super', 'scrypt:32768:8:1$RVN06VZ6PGH6HiZv$a5383b718026a38e08db84fe68694f86a4b8101486f6cbec5df391296e77ac3079111670ed276ff472770dff32d84b08f8e36f46765bfc1d2521a3a9aef7f92', 'supervisor', 1, 'Mauricio', 'Leal');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cdp`
--
ALTER TABLE `cdp`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo` (`codigo`),
  ADD UNIQUE KEY `usuario_id` (`usuario_id`),
  ADD KEY `fk_cdp_red` (`red_id`);

--
-- Indices de la tabla `lider`
--
ALTER TABLE `lider`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_lider_cdp` (`cdp_id`);

--
-- Indices de la tabla `red`
--
ALTER TABLE `red`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_red_supervisor` (`supervisor_id`);

--
-- Indices de la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_reporte_cdp` (`cdp_id`),
  ADD KEY `fk_reporte_lider` (`enviado_por_lider_id`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cdp`
--
ALTER TABLE `cdp`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lider`
--
ALTER TABLE `lider`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `red`
--
ALTER TABLE `red`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cdp`
--
ALTER TABLE `cdp`
  ADD CONSTRAINT `fk_cdp_red` FOREIGN KEY (`red_id`) REFERENCES `red` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_cdp_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `lider`
--
ALTER TABLE `lider`
  ADD CONSTRAINT `fk_lider_cdp` FOREIGN KEY (`cdp_id`) REFERENCES `cdp` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `red`
--
ALTER TABLE `red`
  ADD CONSTRAINT `fk_red_supervisor` FOREIGN KEY (`supervisor_id`) REFERENCES `usuario` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `reporte`
--
ALTER TABLE `reporte`
  ADD CONSTRAINT `fk_reporte_cdp` FOREIGN KEY (`cdp_id`) REFERENCES `cdp` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_reporte_lider` FOREIGN KEY (`enviado_por_lider_id`) REFERENCES `lider` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

```

---

## 5. Priorización por Fases

### Fase 1 — Núcleo y Reportes (Completada en su mayoría)
- [x] Conexión centralizada a base de datos con circuit breaker y fallbacks transparentes.
- [x] Corrección e inserción de reportes (`cdp_service.py` y `db_queries.insertar_reporte` alineados con el esquema SQL).
- [x] Módulo de reportes dinámico para Admin y Supervisor con filtros combinados (texto, red, casa, fechas) y paginación server-side.
- [x] Dashboard multi-nivel conectado a datos reales, filtros jerárquicos y caché.
- [x] Depuración responsive, solución de doble scrollbar y accesibilidad WCAG 2.2 AA/AAA en estructura y reportes.

### Fase 2 — CRUDs Administrativos (Próximo paso prioritario)
- [ ] **CRUD Usuarios**: Listar usuarios reales de BD, formulario crear/editar, activar/desactivar y hasheo seguro de contraseñas.
- [ ] **CRUD Casas de Paz**: Crear, editar, cambiar estado (activa/pausada), asignar usuario y vincular a red.
- [ ] **CRUD Redes**: Crear, editar, pausar, asignar supervisor y gestionar casas asociadas.
- [ ] **CRUD Líderes**: Crear, editar, eliminar y vincular a Casas de Paz (Admin y Supervisor).
- [ ] Incorporación de métodos `POST`, validación de formularios y protección CSRF.

### Fase 3 — Home CDP, Perfil y Notificaciones
- [ ] Historial y resumen dinámico en el panel de Casa de Paz (`index.html`).
- [ ] Módulo de Perfil: Actualización de datos y cambio de contraseña con verificación de clave actual.
- [ ] Sistema de Flash Messages / Toasts globales para retroalimentación de operaciones.

### Fase 4 — Exportación y Polish final
- [ ] Exportación de reportes y listados a PDF y Excel con filtros aplicados.
- [ ] Búsqueda en tiempo real sin recarga en tablas de Usuarios y Líderes.
- [ ] Tooltips interactivos y accesibles en gráficos del dashboard.
- [ ] Configuración segura de producción (variables de entorno obligatorias, `DEBUG=False`, desactivación de modo mock).
