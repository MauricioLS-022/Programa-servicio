from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
import time
import threading
from dotenv import load_dotenv

from config import config
from mock_data import (
    get_redes_demo, get_casas_demo,
    get_mock_generales, get_mock_red, get_mock_cdp,
    get_empty_generales, get_empty_red, get_empty_cdp,
)
from db_queries import get_metricas_generales, get_metricas_red, get_metricas_cdp

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])
app.secret_key = app.config['SECRET_KEY']

# ---------------------------------------------------------------------------
# Fase 1: Circuit Breaker para conexiones a BD
# ---------------------------------------------------------------------------
DB_AVAILABLE = False
_last_db_attempt = 0.0
_db_fail_count = 0
_DB_RETRY_INTERVAL = 15   # segundos entre reintentos si la BD falla
_DB_TIMEOUT = 0.5         # timeout de conexión en segundos (falla instantánea)
_db_lock = threading.Lock()


def get_db_connection():
    """Conexión a MySQL con circuit breaker. Si falla, reintenta cada 30s."""
    global DB_AVAILABLE, _last_db_attempt, _db_fail_count

    with _db_lock:
        ahora = time.time()

        # Si falló recientemente, NO intentar conectar (evita lag de 2-15s)
        if _db_fail_count > 0 and (ahora - _last_db_attempt) < _DB_RETRY_INTERVAL:
            DB_AVAILABLE = False
            return None

        try:
            conn = pymysql.connect(
                host=app.config['DB_HOST'],
                port=app.config['DB_PORT'],
                user=app.config['DB_USER'],
                password=app.config['DB_PASSWORD'],
                database=app.config['DB_NAME'],
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=_DB_TIMEOUT,
                read_timeout=_DB_TIMEOUT,
            )
            DB_AVAILABLE = True
            _db_fail_count = 0
            _last_db_attempt = ahora
            return conn
        except Exception as e:
            _db_fail_count += 1
            _last_db_attempt = ahora
            DB_AVAILABLE = False
            print(f"[DB] No disponible (reintentando en {_DB_RETRY_INTERVAL}s): {e}")
            return None


# ---------------------------------------------------------------------------
# Fase 2: Caché en memoria con TTL para métricas del dashboard
# ---------------------------------------------------------------------------
_dashboard_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 300  # 5 minutos


def _get_cache(key):
    """Retorna valor缓 si existe y no expiró, o None."""
    with _cache_lock:
        entry = _dashboard_cache.get(key)
        if entry and (time.time() - entry['ts']) < _CACHE_TTL:
            return entry['data']
    return None


def _set_cache(key, data):
    """Almacena valor en caché con timestamp."""
    with _cache_lock:
        _dashboard_cache[key] = {'data': data, 'ts': time.time()}


def invalidate_dashboard_cache():
    """Vacía toda la caché del dashboard (llamar al enviar un reporte)."""
    with _cache_lock:
        _dashboard_cache.clear()
    print("[CACHE] Dashboard cache invalidado")


# ---------------------------------------------------------------------------
# Fase 3: Caché de activos estáticos CSS/JS en el navegador
# ---------------------------------------------------------------------------
@app.after_request
def add_static_cache_headers(response):
    """Inyecta cabeceras Cache-Control para archivos estáticos."""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'
        response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            try:
                values['v'] = int(os.stat(file_path).st_mtime)
            except OSError:
                pass
    return url_for(endpoint, **values)


def role_required(*roles):
    def decorator(f):
        def wrapper(*args,**kwargs):
            if "usuario" not in session:
                return redirect(url_for("login"))
            if session.get("rol") not in roles:
                return "No tienes permiso para acceder a esta página"
            return f(*args,**kwargs)
        wrapper.__name__=f.__name__
        return wrapper
    return decorator

@app.route('/',methods=['GET','POST'])
# @role_required("cdp")
def index():
    # Require login
    # if "usuario" not in session:
        # return redirect(url_for("login"))

    # connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
    # C=connect.cursor()
    # try:
        usuario = session.get("usuario")
        rol = session.get("rol")
        return render_template('index.html', usuario=usuario, rol=rol, is_cdp=True)
    # finally:
        # connect.close()

@app.route('/generar_reporte',methods=['GET','POST'])
# @role_required("cdp")
def generar():
    if request.method=='POST':
        anfitrion=request.form['anfitrion']
        ninos=request.form['ninos']
        regulares=request.form['regulares']
        visitas=request.form['visitas']
        comprometidos=request.form['comprometidos']
        asistencia=request.form['asistencia']
        reconciliaciones=request.form['reconciliaciones']
        confesiones=request.form['confesiones']
        cesta=request.form['cesta']
        fecha=request.form['fecha']
        horaini=request.form['horaini']
        horafin=request.form['horafin']
        tema=request.form['tema']
        observaciones=request.form['observaciones']
        ofrendas=request.form['ofrendas']

        # connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
        # C=connect.cursor()

        val=(anfitrion,ninos,regulares,visitas,comprometidos,asistencia,reconciliaciones,confesiones,cesta,fecha,horaini,horafin,tema,observaciones,ofrendas)

        print(val)

        # Invalidar caché del dashboard cuando se envía un reporte
        invalidate_dashboard_cache()

    # Require login for report generation view
    # if "usuario" not in session:
    #     return redirect(url_for("login"))

    usuario = session.get("usuario")
    rol = session.get("rol")
    return render_template('generar_reporte.html', usuario=usuario, rol=rol, is_cdp=True)

# @app.route('/perfil',methods=['GET','POST']) # ruta para vista de perfil de lider
@app.route('/admin/perfil',methods=['GET','POST']) # ruta para vista de perfil de admin
# @app.route('/supervisor/perfil',methods=['GET','POST']) # ruta para vista de perfil de supervisor
@role_required("cdp","admin","supervisor")
def perfil():
    usuario = session["usuario"]
    rol = session["rol"]
    
    connect = get_db_connection()
    if connect:
        try:
            C = connect.cursor()
            # Aquí podrías hacer consultas a la BD
        except Exception as e:
            print(f"[DB] Error perfil: {e}")
        finally:
            connect.close()
    
    return render_template('perfil.html', usuario=usuario, rol=rol, is_admin=True)

@app.route('/admin/usuario')
def admin_usuarios():
    return render_template('usuarios_admin.html', is_admin=True)

@app.route('/admin/usuario/editar')
def editar_usuario():
    return render_template('form_usuario.html', title='Usuarios', breadcrumb= 'Usuario', link='usuario', is_admin=True)

@app.route('/admin/dashboard')
def admin_dashboard():
    nivel = request.args.get('nivel', 'general')

    red_id_str = request.args.get('red_id', '')
    cdp_id_str = request.args.get('cdp_id', '')

    try:
        red_id = int(red_id_str) if red_id_str and red_id_str.isdigit() else None
    except (ValueError, TypeError):
        red_id = None

    try:
        cdp_id = int(cdp_id_str) if cdp_id_str and cdp_id_str.isdigit() else None
    except (ValueError, TypeError):
        cdp_id = None

    usuario = session.get("usuario", "Administrador")
    rol = session.get("rol", "admin")
    is_supervisor = rol == "supervisor"

    conn = get_db_connection()
    db_connected = conn is not None

    # --- Selectores (redes y casas) - también caché ---
    cache_key_selectores = 'selectores'
    cached_selectores = _get_cache(cache_key_selectores)

    if cached_selectores:
        redes, casas = cached_selectores
    elif db_connected:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.id, r.nombre,
                       CONCAT(u.nombre, ' ', u.apellido) AS supervisor
                FROM red r
                LEFT JOIN usuario u ON r.supervisor_id = u.id
                ORDER BY r.nombre
            """)
            redes = cur.fetchall()
            cur.execute("""
                SELECT c.id, c.codigo, c.codigo AS nombre, c.red_id,
                       CONCAT(l.nombre, ' ', l.apellido) AS lider
                FROM cdp c
                LEFT JOIN lider l ON l.cdp_id = c.id AND l.rol = 'Lider'
                ORDER BY c.codigo
            """)
            casas = cur.fetchall()
            cur.close()
            _set_cache(cache_key_selectores, (redes, casas))
        except Exception:
            redes = get_redes_demo()
            casas = get_casas_demo()
    else:
        redes = get_redes_demo()
        casas = get_casas_demo()

    # --- Métricas del dashboard (con caché) ---
    metricas = {}
    mock_used = False
    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}'

    cached_metricas = _get_cache(cache_key)

    if cached_metricas:
        metricas = cached_metricas
        # Si no tenemos conexión, mock_used lo determinamos por si hay DB
        mock_used = not db_connected
    else:
        if nivel == 'general':
            if db_connected:
                try:
                    metricas = get_metricas_generales(conn)
                    _set_cache(cache_key, metricas)
                except Exception as e:
                    print(f"[DB] Error query general: {e}")
                    metricas = get_empty_generales()
                finally:
                    conn.close()
            else:
                metricas = get_mock_generales()
                mock_used = True

        elif nivel == 'red':
            if not red_id:
                red_id = 1
            if db_connected:
                try:
                    result = get_metricas_red(conn, red_id)
                    metricas = result if result else get_empty_red(red_id)
                    _set_cache(cache_key, metricas)
                except Exception as e:
                    print(f"[DB] Error query red: {e}")
                    metricas = get_empty_red(red_id)
                finally:
                    conn.close()
            else:
                metricas = get_mock_red(red_id)
                mock_used = True

        elif nivel == 'cdp':
            if not cdp_id:
                cdp_id = 1
            if db_connected:
                try:
                    result = get_metricas_cdp(conn, cdp_id)
                    metricas = result if result else get_empty_cdp(cdp_id)
                    _set_cache(cache_key, metricas)
                except Exception as e:
                    print(f"[DB] Error query cdp: {e}")
                    metricas = get_empty_cdp(cdp_id)
                finally:
                    conn.close()
            else:
                metricas = get_mock_cdp(cdp_id)
                mock_used = True

    # Si es supervisor, filtrar solo su red
    if is_supervisor and not mock_used:
        redes = redes[:1]

    return render_template(
        'dashboard_admin.html',
        is_admin=True,
        is_supervisor=is_supervisor,
        usuario=usuario,
        nivel=nivel,
        red_id=red_id,
        cdp_id=cdp_id,
        redes=redes,
        casas=casas,
        metricas=metricas,
        db_connected=db_connected,
        mock_used=mock_used,
    )


# ---------------------------------------------------------------------------
# Fase 4: API AJAX para filtros del dashboard (sin recarga completa)
# ---------------------------------------------------------------------------
@app.route('/api/dashboard/datos')
def api_dashboard_datos():
    """Endpoint AJAX que retorna métricas en JSON para filtros dinámicos."""
    nivel = request.args.get('nivel', 'general')
    red_id_str = request.args.get('red_id', '')
    cdp_id_str = request.args.get('cdp_id', '')

    try:
        red_id = int(red_id_str) if red_id_str and red_id_str.isdigit() else None
    except (ValueError, TypeError):
        red_id = None

    try:
        cdp_id = int(cdp_id_str) if cdp_id_str and cdp_id_str.isdigit() else None
    except (ValueError, TypeError):
        cdp_id = None

    conn = get_db_connection()
    db_connected = conn is not None
    cache_key = f'metricas_{nivel}_{red_id}_{cdp_id}'

    cached = _get_cache(cache_key)
    if cached:
        return jsonify(cached)

    metricas = {}
    try:
        if nivel == 'general':
            if db_connected:
                metricas = get_metricas_generales(conn)
            else:
                metricas = get_mock_generales()
        elif nivel == 'red':
            rid = red_id or 1
            if db_connected:
                result = get_metricas_red(conn, rid)
                metricas = result if result else get_empty_red(rid)
            else:
                metricas = get_mock_red(rid)
        elif nivel == 'cdp':
            cid = cdp_id or 1
            if db_connected:
                result = get_metricas_cdp(conn, cid)
                metricas = result if result else get_empty_cdp(cid)
            else:
                metricas = get_mock_cdp(cid)
    except Exception as e:
        print(f"[API] Error: {e}")
    finally:
        if conn:
            conn.close()

    if metricas:
        _set_cache(cache_key, metricas)

    return jsonify(metricas)


@app.route('/admin/estructura')
def admin_estructura():
    return render_template('estructura_admin.html', is_admin=True)

@app.route('/admin/reportes')
def admin_reportes():
    return render_template('reportes_admin.html', is_admin=True)

@app.route('/admin/casa_de_paz/editar')
def editar_cdp():
    return render_template('form_cdp.html', title='Casas de Paz', breadcrumb= 'Casa de paz', link='casa_de_paz', is_admin=True)

@app.route('/admin/casa_de_paz')
def detalles_cdp():
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz', is_admin=True)

@app.route('/admin/red/editar')
def editar_red():
    return render_template('form_redes.html', title='Redes', breadcrumb= 'Red', link='red', is_admin=True)

@app.route('/admin/lider')
def admin_lider():
    return render_template('lider_admin.html', is_admin=True)

@app.route('/admin/lider/editar')
def editar_lider():
    return render_template('form_lider.html', title='Líderes', breadcrumb= 'Lider', link='lider', is_admin=True)

@app.route('/iniciar_sesion',methods=['GET','POST'])
def login():
    p=""

    if request.method=='POST':
        usuario=request.form['usuario']
        contrasena=request.form['contrasena']

        connect = get_db_connection()
        if connect:
            try:
                C = connect.cursor()
                C.execute("SELECT username,tipo_usuario FROM usuario WHERE username = %s and password = %s",(usuario,contrasena))
                r = C.fetchone()

                if not r:
                    p="El usuario no se encuentra registrado"
                else:
                    session["usuario"]=r['username']
                    session["rol"]=r['tipo_usuario']
                    if r['tipo_usuario']=="admin":
                        return redirect(url_for("admin_dashboard"))
                    elif r['tipo_usuario']=="supervisor":
                        return redirect(url_for("supervisor_dashboard"))
                    return redirect(url_for("index"))
            except Exception as e:
                print(f"[DB] Error login: {e}")
                p="Error al verificar credenciales"
            finally:
                connect.close()
        else:
            # Modo demo sin BD: login simulado
            if usuario == "admin" and contrasena == "admin":
                session["usuario"] = "admin"
                session["rol"] = "admin"
                return redirect(url_for("admin_dashboard"))
            elif usuario == "supervisor" and contrasena == "supervisor":
                session["usuario"] = "supervisor"
                session["rol"] = "supervisor"
                return redirect(url_for("supervisor_dashboard"))
            elif usuario and contrasena:
                session["usuario"] = usuario
                session["rol"] = "cdp"
                return redirect(url_for("index"))
            else:
                p="Modo demo: usa admin/admin, supervisor/supervisor o cualquier usuario/contraseña"

    return render_template('login.html',p=p)

@app.route('/logout')
def logout():
    session.pop("usuario",None)
    session.pop("rol",None)
    return redirect(url_for("login"))

@app.route('/supervisor/dashboard')
# @role_required('supervisor')
def supervisor_dashboard():
    # connect = pymysql.connect(host="localhost", user="root", passwd="", database="serv_comunitario")
    # C = connect.cursor()
    # try:
    #     usuario = session["usuario"]
    #     red_id = session.get("red_id")
    #     return render_template('dashboard_admin.html', usuario=usuario, rol=session["rol"], red_id=red_id)
    # finally:
    #     connect.close()
    return render_template('dashboard_admin.html', is_supervisor=True)

@app.route('/supervisor/reportes')
# @role_required('supervisor')
def supervisor_reportes():
    # connect = pymysql.connect(host="localhost", user="root", passwd="", database="serv_comunitario")
    # C = connect.cursor()
    # try:
    #     usuario = session["usuario"]
    #     red_id = session.get("red_id")
    #     return render_template('reportes_admin.html', usuario=usuario, rol=session["rol"], red_id=red_id)
    # finally:
    #     connect.close()
    return render_template('reportes_admin.html', is_supervisor=True)

@app.route('/supervisor/estructura')
# @role_required('supervisor')
def supervisor_estructura():
    # connect = pymysql.connect(host="localhost", user="root", passwd="", database="serv_comunitario")
    # C = connect.cursor()
    # try:
    #     usuario = session["usuario"]
    #     red_id = session.get("red_id")
    #     return render_template('estructura_admin.html', usuario=usuario, rol=session["rol"], red_id=red_id)
    # finally:
    #     connect.close()
    return render_template('estructura_admin.html', is_supervisor=True)

@app.route('/supervisor/lider')
# @role_required('supervisor')
def supervisor_lider():
    # connect = pymysql.connect(host="localhost", user="root", passwd="", database="serv_comunitario")
    # C = connect.cursor()
    # try:
    #     usuario = session["usuario"]
    #     red_id = session.get("red_id")
    #     return render_template('lider_admin.html', usuario=usuario, rol=session["rol"], red_id=red_id)
    # finally:
    #     connect.close()
    return render_template('lider_admin.html', is_supervisor=True)

@app.route('/supervisor/perfil', methods=['GET', 'POST'])
# @role_required('supervisor')
def supervisor_perfil():
    # try:
    #     usuario = session["usuario"]
    #     rol = session["rol"]
    #     return render_template('perfil.html', usuario=usuario, rol=rol, is_supervisor=True)
    # except KeyError:
    #     return redirect(url_for("login"))
    return render_template('perfil.html', is_supervisor=True)
    

@app.route('/perfil', methods=['GET', 'POST'])
# @role_required('supervisor')
def cdp_perfil():

    return render_template('perfil.html', is_cdp=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(
        host=app.config.get('APP_HOST', app.config.get('HOST', '0.0.0.0')),
        port=app.config.get('APP_PORT', app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )
