from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
from dotenv import load_dotenv

from config import config

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[env])
app.secret_key = app.config['SECRET_KEY']

DB_AVAILABLE = False

def get_db_connection():
    """Intenta conectar a MySQL. Si falla, retorna None (modo demo sin BD)."""
    global DB_AVAILABLE
    try:
        conn = pymysql.connect(
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor
        )
        DB_AVAILABLE = True
        return conn
    except Exception as e:
        print(f"[DB] No disponible (modo demo): {e}")
        DB_AVAILABLE = False
        return None

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
    #     return redirect(url_for("login"))

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
    
    if DB_AVAILABLE:
        connect = get_db_connection()
        if connect:
            C = connect.cursor()
            # Aquí podrías hacer consultas a la BD
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
    return render_template('dashboard_admin.html', is_admin=True)

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

        if DB_AVAILABLE:
            connect = get_db_connection()
            if connect:
                C = connect.cursor()
                C.execute("SELECT username,tipo_usuario FROM usuario WHERE username = %s and password = %s",(usuario,contrasena))
                r = C.fetchone()
                connect.close()

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
            else:
                p="Error de conexión a la base de datos"
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
