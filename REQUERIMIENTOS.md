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
  `password` varchar(128) NOT NULL,
  `tipo_usuario` enum('admin','supervisor','cdp') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `nombre` varchar(30) DEFAULT NULL,
  `apellido` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `username`, `password`, `tipo_usuario`, `is_active`, `nombre`, `apellido`) VALUES
('1d4f7c99-7d51-11f1-bf9e-2016d8516279', 'lider', '01234567', 'cdp', 1, 'Mauricio', 'Leal'),
('702f2129-7d4e-11f1-bf9e-2016d8516279', 'admin', '01234567', 'admin', 1, 'Mauricio', 'Leal'),
('ca58cfc6-8337-11f1-8217-2016d8516279', 'super', '01234567', 'supervisor', 1, 'Mauricio', 'Leal');

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
