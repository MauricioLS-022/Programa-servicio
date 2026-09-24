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


