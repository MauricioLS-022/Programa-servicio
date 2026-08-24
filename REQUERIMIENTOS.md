# Requerimientos — Proyecto Vino Nuevo

## Descripción General
Aplicación web de gestión y reportes para un servicio comunitario (ministerio "Vino Nuevo").  
**Stack:** Python Flask + MySQL (PyMySQL) + HTML/CSS (Jinja2)

---

## 1. Estado general de requerimientos

**Criterio:** se considera implementado solo lo que está conectado a una ruta, servicio, consulta o listener funcional. El HTML estático por sí solo se considera maquetado.

| # | Requerimiento | Estado actual | Evidencia y trabajo pendiente |
|---|---|---|---|
| 1 | **INSERT de reportes en BD** | ⚠️ Defectuoso | `services/cdp_service.py` intenta hacer `INSERT`, pero usa nombres de columnas que no coinciden con este esquema (`regulares` vs. `nro_regulares`, `horaini` vs. `hr_inicio`, etc.). No asigna correctamente `cdp_id` ni `enviado_por_lider_id`. |
| 2 | **CRUD de Usuarios** | ❌ Pendiente | `routes/admin_routes.py` solo renderiza plantillas. `usuarios_admin.html` y `form_usuario.html` contienen datos demo y botones sin POST funcional. |
| 3 | **CRUD de Casas de Paz** | ❌ Pendiente | Las rutas de consulta, creación, edición y eliminación no ejecutan operaciones sobre la BD. |
| 4 | **CRUD de Redes** | ❌ Pendiente | `red/editar` solo muestra el formulario; las acciones del menú de estructura usan enlaces `#`. |
| 5 | **CRUD de Líderes** | ❌ Pendiente | `lider_admin.html` muestra filas estáticas y `lider/editar` no procesa formularios. |
| 6 | **Dashboard con datos reales** | ✅ Parcialmente cumplido | `dashboard_service.py` y `db_queries.py` tienen consultas reales, métricas por nivel, filtros jerárquicos, modo mock y estados vacíos. Debe verificarse y completar la consistencia de todas las métricas. |
| 7 | **Vista de reportes enviados para CDP** | ✅ Maquetado / ⚠️ Datos demo | `index.html` ya tiene dashboard, acceso a nuevo reporte y estado vacío, pero sus métricas, historial y equipo están hardcodeados. |
| 8 | **Filtros de reportes** | ❌ Pendiente | `reportes_admin.html` tiene controles visuales sin `name`, `action` ni backend para buscar por texto, red, CDP o fechas. |
| 9 | **Paginación real** | ❌ Pendiente | Los controles de paginación de reportes y líderes son decorativos y no consultan páginas en BD. |
| 10 | **Exportar PDF/Excel** | ❌ Pendiente | Los botones existen, pero no hay endpoints ni generación de archivos. El dashboard usa un `alert()` simulado. |
| 11 | **Búsqueda en tiempo real** | ⚠️ Parcial | El dashboard busca en selectores y puede enviar el formulario. Usuarios, líderes y estructura tienen inputs visuales sin filtrado conectado. |
| 12 | **Flash messages y toasts** | ❌ Pendiente | Solo existe un `flash()` para accesos no autorizados en `utils/auth.py`. Los layouts no renderizan mensajes y los CRUD no los generan. |
| 13 | **Contactar por WhatsApp** | ⚠️ Parcial | El dashboard general construye enlaces `wa.me` usando el teléfono del líder. La alerta zonal no devuelve el teléfono y falta normalización robusta del número. |
| 14 | **Gestión de contraseña** | ❌ Pendiente | El login usa hashes Werkzeug, pero el perfil solo muestra usuario y rol; no existe formulario ni ruta para cambiar contraseña. |
| 15 | **Vistas de supervisor** | ⚠️ Parcial | Dashboard y estructura tienen rutas, autorización y aislamiento por red. Reportes y líderes solo renderizan maquetas sin contexto de BD. |

### Funcionalidades ya cumplidas o disponibles

- Login con validación de hashes Werkzeug y migración de contraseñas legacy después de un acceso válido.
- Decoradores de autenticación, autorización por rol y validación de propiedad de la URL.
- Conexión centralizada a MySQL mediante `database.py`, con circuit breaker y cierre de conexiones en los servicios principales.
- Dashboard con vistas general, red y Casa de Paz.
- Consultas agregadas para asistencia, ofrendas, conversiones, rankings, tendencias y alertas.
- Modo mock explícito para desarrollo y estados vacíos cuando la BD está disponible pero no tiene datos.
- Navegación responsive con sidebar, header móvil y barra inferior móvil.
- Filtros locales de redes en la vista de estructura.

### Inconsistencias técnicas confirmadas

- El formulario de reporte envía `lider_id`, pero la ruta no lo procesa y el servicio espera `anfitrion`.
- El servicio de reportes intenta insertar columnas que no aparecen en la tabla `reporte` documentada.
- La home CDP usa enlaces hardcodeados como `/generar_reporte` y `/historial` en lugar de rutas con `url_for()`.
- Las rutas admin de edición no incluyen métodos `POST` ni identificadores de entidad para distinguir creación y edición.
- `api_routes.py` abre una conexión para comprobar disponibilidad y no la cierra.
- La API de dashboard no valida explícitamente sesión ni rol.
- El esquema SQL no contiene `email`, aunque algunos helpers de perfil intentan consultarlo y actualizarlo.

---

## 2. Problemas de seguridad

| # | Problema | Estado / severidad | Detalle |
|---|---|---|---|
| 1 | **Contraseñas en texto plano** | ✅ Resuelto parcialmente | El login valida hashes Werkzeug y migra registros legacy. Debe asegurarse que todos los nuevos usuarios se creen siempre con hash y que no se expongan contraseñas en formularios. |
| 2 | **Sin protección CSRF** | 🔴 Alta / Pendiente | Los formularios POST no incluyen tokens CSRF. Integrar Flask-WTF o una protección equivalente antes de activar los CRUD. |
| 3 | **Credenciales de BD por defecto** | 🟡 Media / Pendiente | `config.py` permite usuario `root` y contraseña vacía por defecto. En producción deben ser obligatorias las variables de entorno y una cuenta con permisos mínimos. |
| 4 | **Manejo de conexiones** | ⚠️ Parcial | La mayoría de servicios usa `finally` para cerrar conexiones, pero todavía deben revisarse API, cursores y cualquier nueva operación CRUD. |
| 5 | **Debug habilitado por defecto** | 🟡 Media / Pendiente | `DEBUG` y desarrollo están activos por defecto. La configuración de producción debe impedir trazas y secretos de desarrollo. |
| 6 | **Modo demo permisivo** | 🟡 Media / Pendiente | Cuando no hay BD, el login acepta cualquier usuario y contraseña como CDP. Debe limitarse estrictamente a desarrollo y no estar disponible en producción. |
| 7 | **API sin autorización explícita** | 🟡 Media / Pendiente | `/api/dashboard/datos` debe exigir sesión, rol permitido y aplicar el aislamiento de red del supervisor. |
| 8 | **Ausencia de validación de entrada** | 🟡 Media / Pendiente | Formularios y parámetros deben validar tipos, rangos numéricos, fechas, relaciones existentes y errores de duplicados antes de persistir. |

---

## 3. Mejoras UI/UX

| # | Mejora | Estado actual | Trabajo pendiente |
|---|---|---|---|
| 1 | **Home CDP** | ✅ Maquetada / ⚠️ Parcial | Ya tiene contenido visual y estado vacío; falta cargar métricas, historial y equipo reales. |
| 2 | **Responsive en móviles** | ⚠️ Parcial | Existen contenedores `.table-responsive` y estilos responsive; verificar que todas las tablas apliquen `overflow-x: auto` y no usen datos rígidos. |
| 3 | **Estados vacíos** | ⚠️ Parcial | Dashboard y estructura ya tienen estados vacíos. Reportes, usuarios y líderes deben mostrar estados basados en resultados reales. |
| 4 | **Feedback de botones copiar** | ❌ Pendiente | Implementar Clipboard API, cambio temporal a icono de confirmación y mensaje accesible. |
| 5 | **Tooltips del gráfico donut** | ⚠️ Parcial | La leyenda tiene `title` y cambia el número central al hacer hover; falta tooltip visual y soporte de interacción directa sobre los segmentos. |
| 6 | **Eliminar medidor redundante** | ❌ Pendiente | Definir y retirar únicamente la barra que duplica el cumplimiento; usar el espacio para mostrar casas pendientes de reportar. |
| 7 | **Búsqueda sin recargar** | ⚠️ Parcial | Dashboard funciona de forma limitada. Conectar búsqueda en usuarios, líderes, estructura y reportes. |
| 8 | **Sidebar móvil** | ✅ Parcialmente cumplido | El menú móvil, overlay y bottom nav existen. Debe probarse en 375px, 768px y con navegación completa del supervisor. |
| 9 | **Mensajes de operación** | ❌ Pendiente | Renderizar `get_flashed_messages()` en los layouts y generar mensajes de éxito/error en todas las operaciones. |
| 10 | **Consistencia de enlaces y botones** | ❌ Pendiente | Reemplazar `href="#"`, `alert()` y URLs hardcodeadas por rutas Flask y acciones reales. |
| 11 | **CSS duplicado** | 🟡 Baja / Pendiente | Revisar variables y estilos repetidos entre `style.css` y `admin.css` después de terminar las funciones principales. |
| 12 | **Nombres de archivos** | 🟡 Baja / Pendiente | Evitar espacios en nuevos nombres y migrar gradualmente nombres legacy sin romper rutas existentes. |

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

### Fase 1 — Corrección del núcleo
1. Confirmar que la BD instalada coincide con el esquema de este documento
2. Corregir el INSERT de reportes y relacionarlo con `cdp_id` y `enviado_por_lider_id`
3. Alinear nombres de campos del formulario, servicio y tabla `reporte`
4. Validar tipos, rangos, fechas y relaciones antes de guardar
5. Revisar cierre de conexiones y cursores en todos los endpoints
6. Mantener el login con hashes Werkzeug y eliminar cualquier creación de usuarios en texto plano

### Fase 2 — CRUD completo
7. CRUD Usuarios: listar, crear, editar, activar/desactivar y eliminar
8. CRUD Casas de Paz: crear, editar, eliminar y vincular usuario/red
9. CRUD Redes: crear, editar, eliminar y asignar supervisor
10. CRUD Líderes: crear, editar, eliminar y vincular Casa de Paz
11. Incorporar POST, PRG, validaciones y flash messages en cada operación

### Fase 3 — Dashboard y reportes
12. Completar la home CDP con historial, resumen y equipo reales
13. Construir la vista de reportes con consultas y joins reales
14. Implementar filtros por texto, red, Casa de Paz y rango de fechas
15. Implementar paginación server-side
16. Completar reportes y líderes del supervisor con aislamiento por red
17. Proteger API y endpoints de consulta con sesión, rol y permisos

### Fase 4 — UX y polish
18. Renderizar toasts de éxito y error en layouts y formularios
19. Agregar estados vacíos a reportes, usuarios y líderes
20. Implementar búsqueda local sin recarga en tablas y estructura
21. Implementar feedback de copiado de credenciales
22. Mejorar tooltips e interacción accesible del gráfico donut
23. Retirar el medidor redundante y mostrar casas pendientes de reporte
24. Completar responsive de tablas y navegación móvil
25. Reemplazar enlaces `#`, `alert()` y URLs hardcodeadas por acciones reales

### Fase 5 — Seguridad y operación
26. Integrar protección CSRF en formularios POST
27. Hacer obligatorias las credenciales de producción mediante variables de entorno
28. Desactivar debug y modo demo en producción
29. Agregar cambio de contraseña con hash y verificación de contraseña actual
30. Implementar exportación PDF/Excel con permisos y filtros aplicados
31. Actualizar este documento después de cada fase completada
