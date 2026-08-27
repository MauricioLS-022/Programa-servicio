# 🍷 Sistema de Gestión y Reportes de Casas de Paz — Vino Nuevo

> **Proyecto de Servicio Comunitario**  
> **Institución:** Universidad Nacional Experimental de Guayana (**UNEG**)  
> **Organización Beneficiaria:** Iglesia "Vino Nuevo"

---

## 📌 Descripción del Proyecto

Este sistema web ha sido desarrollado en el marco del **Servicio Comunitario de la UNEG** con el objetivo de modernizar, centralizar y optimizar el proceso de recolección y análisis de reportes de las **Casas de Paz (CDP)** de la iglesia **Vino Nuevo**.

### 🎯 Problemática que Soluciona

* **Situación previa:** Anteriormente, los reportes semanales de las Casas de Paz se realizaban y consolidaban de forma manual en hojas de cálculo de Excel. Los encargados debían transcribir reporte por reporte de manera individual, lo cual resultaba en un proceso lento, propenso a errores humanos, demoras en el reporte general y riesgo de inconsistencia o pérdida de datos.
* **Solución desarrollada:** Se diseñó e implementó una plataforma web ágil e intuitiva donde:
  - Los líderes de Casa de Paz pueden registrar sus reportes semanales (asistencia de adultos, niños, nuevos convertidos, reconciliaciones, ofrendas y detalles de la reunión) directamente desde cualquier dispositivo móvil o computador.
  - La administración y supervisores tienen acceso inmediato a un **Dashboard en tiempo real**, visualizando métricas consolidadas, estadísticas de crecimiento, comparativas por redes y estado de cumplimiento sin necesidad de transcripción manual.

---

## ✨ Características Principales

- 📱 **Diseño 100% Responsivo:** Interfaz adaptada tanto para teléfonos móviles (líderes en campo) como para computadoras (panel administrativo).
- 📊 **Panel de Control (Dashboard):** Métricas clave automáticas (total de asistentes, niños, nuevos convertidos, ofrendas, tendencias semanales y cumplimiento de reportes).
- 👥 **Control de Acceso Basado en Roles:**
  - **Administrador:** Control total de métricas, directorio de usuarios, líderes, redes y Casas de Paz.
  - **Supervisor de Red:** Supervisión y seguimiento de las CDP y líderes adscritos a su red específica.
  - **Líder de CDP:** Formulario de envío y consulta de sus reportes.
- 🗂️ **Gestión de Directorio:** Módulos CRUD para usuarios, líderes, redes y Casas de Paz con filtros de búsqueda y paginación.
- ⚡ **Resiliencia con Circuit Breaker:** El sistema detecta automáticamente el estado de la base de datos MySQL e incluye un mecanismo de contingencia para evitar bloqueos.
- 🎨 **Design System Coherente:** Estética visual personalizada y unificada acorde a la identidad institucional de la iglesia Vino Nuevo.

---

## 🛠️ Stack Tecnológico

- **Backend:** [Python 3.10+](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/)
- **Base de Datos:** [MySQL](https://www.mysql.com/) / MariaDB (conectado mediante `PyMySQL` / `mysqlclient`)
- **Frontend / Plantillas:** HTML5 semántico, CSS3 moderno, Jinja2, Google Fonts (Manrope, Noto Serif) y Material Symbols Outlined.
- **Entorno y Seguridad:** `python-dotenv` para variables de entorno, sesiones seguras y control de accesos.
- **Servidor de Producción:** Compatible con Gunicorn.

---

## 📋 Requisitos del Sistema

Antes de ejecutar el proyecto, asegúrate de contar con:

1. **Python:** Versión 3.10 o superior.
2. **Pip:** Gestor de paquetes de Python (incluido por defecto con Python).
3. **Servidor MySQL / MariaDB:** (Por ejemplo: MySQL Server local, XAMPP, WampServer o una base de datos remota).
4. **Git:** (Opcional, para clonar el repositorio).

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

### 1. Clonar o descargar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd "Programa servicio"
```

### 2. Crear y activar un entorno virtual

* **En Windows (PowerShell / CMD):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
Con el entorno virtual activado, ejecuta:
```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno
Crea un archivo `.env` en la raíz del proyecto tomando como referencia el archivo `example.env`:

* **En Windows (PowerShell):**
  ```powershell
  Copy-Item example.env .env
  ```
* **En Linux / macOS:**
  ```bash
  cp example.env .env
  ```

Edita el archivo `.env` con las credenciales de tu entorno:
```env
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=serv_comunitario

APP_HOST=0.0.0.0
APP_PORT=5000
DEBUG=True
```

### 5. Configurar la Base de Datos
Asegúrate de que el servicio de MySQL esté corriendo (por ejemplo, desde el panel de XAMPP) y que exista la base de datos correspondiente (`serv_comunitario` o el nombre configurado en tu `.env`).

### 6. Ejecutar la aplicación
Inicia el servidor de desarrollo ejecutando:
```bash
python app.py
```

### 7. Acceder a la plataforma
Abre tu navegador web y visita:
```
http://localhost:5000
```
*(O `http://127.0.0.1:5000`)*

---

## 📁 Estructura del Proyecto

```text
├── app.py                  # Punto de entrada principal e inicialización de Flask
├── config.py               # Configuraciones por entorno (desarrollo / producción)
├── database.py             # Gestión de conexión MySQL y Circuit Breaker
├── db_queries.py           # Consultas SQL para dashboards, reportes y métricas
├── example.env             # Plantilla de variables de entorno
├── requirements.txt        # Dependencias del proyecto Python
├── routes/                 # Controladores y Blueprints modulares
│   ├── admin_routes.py     # Rutas del panel administrativo
│   ├── auth_routes.py      # Autenticación (Login, Logout)
│   ├── cdp_routes.py       # Rutas para el reporte y gestión de Casas de Paz
│   ├── supervisor_routes.py# Rutas del panel de supervisores
│   └── api_routes.py       # Endpoints auxiliares
├── services/               # Lógica de negocio desacoplada
├── static/                 # Recursos estáticos (CSS, scripts JS, iconos, logos)
│   ├── styles/             # Hojas de estilo y design system
│   └── scripts/            # Scripts interactivos para la interfaz
├── templates/              # Vistas y plantillas Jinja2
└── utils/                  # Decoradores, helpers y filtros de contexto
```

---

## 💡 Aspectos Importantes a Considerar

1. **Variables de Entorno:** Nunca subas el archivo `.env` real al repositorio de control de versiones para proteger las contraseñas y claves secretas.
2. **Circuit Breaker:** Si MySQL no está disponible temporalmente, la aplicación no colapsa; maneja los reintentos controlados para mantener la experiencia de usuario fluida.
3. **Cache Busting:** Los recursos estáticos cuentan con versionado automático para asegurar que los navegadores carguen siempre los cambios más recientes en estilos y scripts.
4. **Mantenimiento y Escalabilidad:** La arquitectura desacoplada en *Blueprints* y *Services* permite extender fácilmente nuevas funcionalidades (ej. exportación en PDF/Excel, reportes históricos avanzados o notificaciones).

---

## 🎓 Créditos y Reconocimientos

* **Proyecto:** Servicio Comunitario UNEG.
* **Universidad:** Universidad Nacional Experimental de Guayana (UNEG).
* **Comunidad Beneficiaria:** Iglesia Vino Nuevo.