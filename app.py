from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import os
#from dotenv import load_dotenv
#import requests
#from requests.auth import HTTPBasicAuth

app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY")

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
@role_required("cdp")
def index():
    connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
    C=connect.cursor()

    return render_template('index.html')

@app.route('/generar_reporte',methods=['GET','POST'])
@role_required("cdp","admin","supervisor")
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

        connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
        C=connect.cursor()

        val=(anfitrion,ninos,regulares,visitas,comprometidos,asistencia,reconciliaciones,confesiones,cesta,fecha,horaini,horafin,tema,observaciones,ofrendas)

        print(val)

    return render_template('generar reporte.html')

@app.route('/perfil',methods=['GET','POST']) # ruta para vista de perfil de lider
@app.route('/admin/perfil',methods=['GET','POST']) # ruta para vista de perfil de admin
@role_required("cdp","admin","supervisor")
def perfil():
    connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
    C=connect.cursor()

    usuario=session["usuario"]
    rol=session["rol"]

    return render_template('perfil.html',usuario=usuario,rol=rol)

@app.route('/admin')
@role_required('admin')
def admin():
    connect = pymysql.connect(host='localhost', user = 'root', passwd='', database='serv_comunitario')
    c = connect.cursor()

    usuario=session["usuario"]
    rol=session["rol"]
    return render_template('admin_layout.html',usuario=usuario,rol=rol)

@app.route('/admin/usuario')
def admin_usuarios():
    return render_template('usuarios_admin.html')

@app.route('/admin/usuario/editar')
def editar_usuario():
    return render_template('form_usuario.html', title='Usuarios', breadcrumb= 'Usuario', link='usuario')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('dashboard_admin.html')

@app.route('/admin/estructura')
def admin_estructura():
    return render_template('estructura_admin.html')

@app.route('/admin/reportes')
def admin_reportes():
    return render_template('reportes_admin.html')

@app.route('/admin/casa_de_paz/editar')
def editar_cdp():
    return render_template('form_cdp.html', title='Casas de Paz', breadcrumb= 'Casa de paz', link='casa_de_paz')

@app.route('/admin/casa_de_paz')
def detalles_cdp():
    return render_template('detalles_cdp.html', title='Detalles de Casa de Paz', breadcrumb='Casa de paz', link='casa_de_paz')

@app.route('/admin/red/editar')
def editar_red():
    return render_template('form_redes.html', title='Redes', breadcrumb= 'Red', link='red')

@app.route('/admin/lider')
def admin_lider():
    return render_template('lider_admin.html')

@app.route('/admin/lider/editar')
def editar_lider():
    return render_template('form_lider.html', title='Líderes', breadcrumb= 'Lider', link='lider')

@app.route('/iniciar_sesion',methods=['GET','POST'])
def login():
    p=""

    if request.method=='POST':
        usuario=request.form['usuario']
        contrasena=request.form['contrasena']

        connect=pymysql.connect(host="localhost",user="root",passwd="",database="serv_comunitario")
        C=connect.cursor()

        C.execute("SELECT username,tipo_usuario FROM usuario WHERE username = %s and password = %s",(usuario,contrasena))

        r=C.fetchone()

        if not r:
            p="El usuario no se encuentra registrado"
        else:
            session["usuario"]=r[0]
            session["rol"]=r[1]
            if r[1]=="admin":
                return redirect(url_for("admin"))
            return redirect(url_for("index"))

    return render_template('login.html',p=p)

@app.route('/logout')
def logout():
    session.pop("usuario",None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
