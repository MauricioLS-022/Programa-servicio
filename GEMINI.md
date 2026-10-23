# Reglas de Comportamiento del Proyecto

## 1. Modificación de Archivos y Confirmación Previa
* **Consultas y Preguntas**:
  * Si el usuario realiza una consulta, pregunta o análisis sobre un archivo, flujo o componente, responder directamente y con precisión sin alterar ningún archivo.
  * No solicitar confirmaciones innecesarias cuando el usuario solo está consultando información.
  * Si durante una consulta se detecta un posible ajuste, mejora o error, explicar el hallazgo en la respuesta y preguntar primero si desea que se realice la modificación.
* **Confirmación Única antes de Editar**:
  * Antes de realizar cualquier cambio, creación o eliminación de archivos, solicitar confirmación al usuario resumiendo brevemente qué archivos y cambios se van a realizar.
  * **Regla de confirmación única**: Preguntar **una sola vez** para todo el conjunto de archivos involucrados en la tarea, NUNCA preguntar archivo por archivo.
  * Proceder con las modificaciones únicamente tras recibir la aprobación del usuario.

## 2. Sincronización de REQUERIMIENTOS.md antes de Commits
* Antes de preparar, confirmar o ejecutar cualquier commit en Git:
  * Verificar obligatoriamente si el archivo `REQUERIMIENTOS.md` refleja fielmente los cambios realizados (nuevas características, endpoints, correcciones, candados de seguridad, pruebas automatizadas o estado del roadmap).
  * Si hubo modificaciones en el alcance o estado de los requerimientos, actualizar `REQUERIMIENTOS.md` para que quede incluido en el commit correspondiente.

## 3. Gestor de Paquetes Frontend (Node.js) y Versionado
* **Uso exclusivo de `pnpm`**:
  * Para cualquier operación de dependencias o ejecución de scripts en el directorio `frontend/`, se debe utilizar obligatoriamente `pnpm` (p. ej., `pnpm install`, `pnpm add <paquete>`, `pnpm run <script>`, `pnpm test`, `pnpm build`, `pnpm dlx`).
  * Queda estrictamente prohibido el uso de `npm`, `npx` o `yarn` en el frontend para evitar discrepancias de resolución de dependencias y duplicidad de archivos lock.
  * Mantener actualizado `pnpm-lock.yaml` y no generar ni mantener `package-lock.json`.
* **Versiones exactas obligatorias (Sin rangos `^` o `~`)**:
  * Todas las dependencias (`dependencies` y `devDependencies`) en `frontend/package.json` deben declararse con versión exacta fija (ej: `"react": "19.3.1"`).
  * Queda prohibido el uso de prefijos de versión como `^` (caret) o `~` (tilde).
  * Al instalar nuevas dependencias, se debe utilizar la bandera de guardado exacto (`pnpm add --save-exact` o tener configurado `save-exact=true` en `.npmrc`).

## 4. Desarrollo de Vistas Frontend (React) y Paridad con Jinja2
* **Inspección Obligatoria de Plantillas Jinja2**:
  * Antes de crear, modificar o migrar cualquier vista, pantalla o componente en React (`frontend/src/pages/` o `frontend/src/components/`), es **estrictamente obligatorio** revisar previamente la plantilla Jinja equivalente en `backend/templates/` (ej. `detalles_cdp.html`, `usuarios_admin.html`, `lider_admin.html`, `perfil.html`, formularios `form_*.html`).
  * La plantilla Jinja es la base funcional canónica y define el conjunto de datos que debe mostrarse, jerarquías, validaciones, filtros, estados vacíos y roles autorizados.
* **Contrato y Comportamiento de Gesta de Datos (Resiliencia y Circuit Breaker)**:
  * Las vistas en React deben alinearse al comportamiento funcional y contractual de la app original.
  * Integrar y respetar la resiliencia del sistema: manejar estados de carga (skeletons/spinners), estados vacíos (`empty states`), fallbacks de datos y mensajes descriptivos cuando el backend opere en modo degradado, modo mock o cuando el Circuit Breaker (`database.py`) se encuentre en estado `OPEN` o `HALF_OPEN` (errores de conectividad o HTTP 500/503).
  * La interfaz nunca debe congelarse, romperse ni mostrar pantallas en blanco ante fallos de conexión.
* **Reutilización Estricta de Componentes y Tokens**:
  * Utilizar y priorizar en la medida de lo posible los componentes ya existentes en `frontend/src/components/ui/` (`Button`, `Card`, `Input`, `Select`, `Modal`, `Icon`), `frontend/src/components/layout/` y subcomponentes modulares.
  * No crear componentes duplicados si ya existe uno funcional que cumpla la misma tarea.
  * Mantener la identidad visual institucional utilizando los tokens y variables CSS existentes (`--color1` a `--color5`, `--bg-surface`, `--primary`, `--font-body`, scrollbars de 5px con `scrollbar-gutter: stable`).
* **Prevención y Aislamiento de Conflictos de Estilos**:
  * Tomar estilos y variables existentes teniendo en cuenta que algunas hojas de estilo previas (`style.css`, `admin.css`, `dashboard.css`, Tailwind CSS) presentan solapamientos o conflictos de especificidad.
  * Aislar adecuadamente las clases o componentes nuevos para evitar que selectores globales heredados alteren el comportamiento visual de otras pantallas y viceversa.

