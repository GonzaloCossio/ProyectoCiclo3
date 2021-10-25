import functools
import os
from flask import Flask, render_template, flash, request, redirect, url_for,session,g,make_response

from db import get_db, close_db
import utils
from re import X
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app=Flask(__name__)
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

@app.route('/log_in',methods=["GET","POST"])
@app.route('/',methods=["GET","POST"])
def  log_in(): 
    #try:
        if g.user:
            return redirect( url_for( 'inicio' ) )
        if request.method == 'POST':
            db = get_db()
            error = None
            username = request.form['correo']
            password = request.form['password']

            if not username:
                error = 'Debes ingresar el correo'
                flash( error )
                return render_template('log_in.html')

            if not password:
                error = 'Debes ingresar una contraseña'
                flash( error )
                return render_template('log_in.html')
    
            user = db.execute(
                'SELECT * FROM usuario WHERE correo = ? AND contrasena = ?', (username, password)
            ).fetchone()

            if user is None:
                user = db.execute(
                    'SELECT * FROM usuario WHERE correo = ?', (username,)
                ).fetchone()
                if user is None:
                    error1 = 'Usuario no existe'
                    flash( error1 )
                    return render_template('register.html')
                else:
                    #Validar contraseña hash            
                    store_password = user[4]
                    result = check_password_hash(store_password, password)
                    if result is False:
                        error = 'Contraseña inválida'
                        flash( error )
                        return render_template('log_in.html')
                    else:
                        session.clear()
                        session['user_id'] = user[0]
                        resp = make_response( redirect( url_for( 'inicio' ) ) )
                        resp.set_cookie( 'username', username )
                        return resp
            else:
                session.clear()
                session['user_id'] = user[0]
                return redirect( url_for( 'inicio' ) )

        else:
            return render_template( 'log_in.html' )
    #except Exception as e:
    #   print(e)
    #    return render_template( 'login.html' )

@app.route('/register',methods=["GET","POST"])
def  register():
    if g.user:
        return redirect(url_for('inicio'))
    #try:
    if request.method == 'POST':
        name= request.form['nombre']
        celular=request.form['celular']
        email = request.form['correo']
        password = request.form['password']
        ConPassword = request.form['ConPassword']
        condiciones = request.form.get('condiciones')
        promociones=request.form.get('promociones')

        error = None

        db = get_db()

        if not condiciones:
            error = "Debe haber aceptado las condiciones generales del programa y la normativa sobre protección de datos"
            flash(error)

        if not utils.isPasswordValid( password ):
            error = 'La contraseña debe contenir al menos una minúscula, una mayúscula, un número, 8 caracteres y un caracter especial'
            flash( error )

        if not password==ConPassword:
            error= 'Las contraseñas no coinciden'
            flash( error )

        if not utils.isEmailValid( email ):
            error = 'Correo invalido'
            flash( error )
        
        if db.execute( 'SELECT id FROM usuario WHERE correo = ?', (email,) ).fetchone() is not None:
            error = 'El correo ya existe'.format( email )
            flash( error )

        if error is not None:
            return render_template('register.html')
        else:
            rol='usuario'
            if promociones:
                promo=1
            else:
                promo=0
            db.execute(
                'INSERT INTO usuario (nombre, telefono, correo, contrasena, promo, rol) VALUES (?,?,?,?,?,?)',
                (name,celular, email, generate_password_hash(password),promo,rol)
            )
            db.commit()
            #yag = yagmail.SMTP('micuenta@gmail.com', 'clave') #modificar con tu informacion personal
            #yag.send(to=email, subject='Activa tu cuenta',
            #   contents='Bienvenido, usa este link para activar tu cuenta ')
            #flash( 'Revisa tu correo para activar tu cuenta' )
            return redirect( 'log_in' )
    else:
        return render_template('register.html')
    #except:
    #    return render_template( 'register.html' )

def login_required(view): # usuario requerido , es como si estuviese llamando directamente a la funcion interna
    @functools.wraps( view )
    def wrapped_view(**kwargs): # toma una funcion utilizada en un decorador y añadir la funcion de copia el nombre de la funcion
        if g.user is None:
            return redirect( url_for( 'log_in' ) )

        return view( **kwargs )

    return wrapped_view

@app.before_request
def load_logged_in_user():
    print('entro a app.antes_request')
    user_id = session.get( 'user_id' ) #get es para devolver valores de un diccionario
    if user_id is None:
        g.user = None
        print('g.user : ',g.user)
    else: #trae una tupla
        g.user = get_db().execute( 
            'SELECT * FROM usuario WHERE id = ?', (user_id,)
        ).fetchone()

@app.route('/inicio', methods=["GET","POST"])
@login_required
def  inicio():
    return  render_template('inicio.html')

@app.route('/producto', methods=["GET", "POST"])
@login_required
def  producto():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    if request.method=="POST":
        calificacion=request.form.get("grade")
        comentario=request.form["comentario"]
        if not calificacion:
            error = 'Debes calificar el producto'
            flash( error )
            return render_template('/producto.html',producto=producto)
        if not comentario:
            error = 'Debes ingresar un comentario'
            flash( error )
            return render_template('/producto.html',producto=producto)
        db.execute(
                'INSERT INTO comentario (usuario_id, producto_id, mensaje, calificacion) VALUES (?,?,?,?)',
                (g.user[0],producto[0], comentario, calificacion)
        )
        db.commit()
    return  render_template('producto.html',producto=producto)

@app.route('/producto1', methods=["GET", "POST"])
@login_required
def  producto1():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    if request.method=="POST":
        calificacion=request.form.get("grade")
        comentario=request.form["comentario"]
        if not calificacion:
            error = 'Debes calificar el producto'
            flash( error )
            return render_template('/producto.html',producto=producto)
        if not comentario:
            error = 'Debes ingresar un comentario'
            flash( error )
            return render_template('/producto.html',producto=producto)
        db.execute(
                'INSERT INTO comentario (usuario_id, producto_id, mensaje, calificacion) VALUES (?,?,?,?)',
                (g.user[0],producto[0], comentario, calificacion)
        )
        db.commit()
    return  render_template('producto.html',producto=producto)

@app.route('/producto2', methods=["GET", "POST"])
@login_required
def  producto2():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (2,)).fetchone()
    if request.method=="POST":
        calificacion=request.form.get("grade")
        comentario=request.form["comentario"]
        if not calificacion:
            error = 'Debes calificar el producto'
            flash( error )
            return render_template('/producto.html',producto=producto)
        if not comentario:
            error = 'Debes ingresar un comentario'
            flash( error )
            return render_template('/producto.html',producto=producto)
        db.execute(
                'INSERT INTO comentario (usuario_id, producto_id, mensaje, calificacion) VALUES (?,?,?,?)',
                (g.user[0],producto[0], comentario, calificacion)
        )
        db.commit()
    return  render_template('producto.html',producto=producto)

@app.route('/producto3', methods=["GET", "POST"])
@login_required
def  producto3():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (3,)).fetchone()
    if request.method=="POST":
        calificacion=request.form.get("grade")
        comentario=request.form["comentario"]
        if not calificacion:
            error = 'Debes calificar el producto'
            flash( error )
            return render_template('/producto.html',producto=producto)
        if not comentario:
            error = 'Debes ingresar un comentario'
            flash( error )
            return render_template('/producto.html',producto=producto)
        db.execute(
                'INSERT INTO comentario (usuario_id, producto_id, mensaje, calificacion) VALUES (?,?,?,?)',
                (g.user[0],producto[0], comentario, calificacion)
        )
        db.commit()
    return  render_template('producto.html',producto=producto)

@app.route('/producto4', methods=["GET", "POST"])
@login_required
def  producto4():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (4,)).fetchone()
    if request.method=="POST":
        calificacion=request.form.get("grade")
        comentario=request.form["comentario"]
        if not calificacion:
            error = 'Debes calificar el producto'
            flash( error )
            return render_template('/producto.html',producto=producto)
        if not comentario:
            error = 'Debes ingresar un comentario'
            flash( error )
            return render_template('/producto.html',producto=producto)
        db.execute(
                'INSERT INTO comentario (usuario_id, producto_id, mensaje, calificacion) VALUES (?,?,?,?)',
                (g.user[0],producto[0], comentario, calificacion)
        )
        db.commit()
    return  render_template('producto.html',producto=producto)

@app.route('/wishlist', methods=["GET","POST"])
@login_required
def  wishlist():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    return  render_template('wishlist.html',producto=producto)

@app.route('/wishlist1', methods=["GET","POST"])
@login_required
def  wishlist1():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    return  render_template('wishlist.html',producto=producto)

@app.route('/wishlist2', methods=["GET","POST"])
@login_required
def  wishlist2():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (2,)).fetchone()
    return  render_template('wishlist.html',producto=producto)

@app.route('/wishlist3', methods=["GET","POST"])
@login_required
def  wishlist3():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (3,)).fetchone()
    return  render_template('wishlist.html',producto=producto)

@app.route('/wishlist4', methods=["GET","POST"])
@login_required
def  wishlist4():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (4,)).fetchone()
    return  render_template('wishlist.html',producto=producto)

@app.route('/comprar', methods=["GET","POST"])
@login_required
def  comprar():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    return  render_template('comprar.html',producto=producto)

@app.route('/comprar1', methods=["GET","POST"])
@login_required
def  comprar1():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (1,)).fetchone()
    return  render_template('comprar.html',producto=producto)

@app.route('/comprar2', methods=["GET","POST"])
@login_required
def  comprar2():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (2,)).fetchone()
    return  render_template('comprar.html',producto=producto)

@app.route('/comprar3', methods=["GET","POST"])
@login_required
def  comprar3():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (3,)).fetchone()
    return  render_template('comprar.html',producto=producto)

@app.route('/comprar4', methods=["GET","POST"])
@login_required
def  comprar4():
    db = get_db()
    producto = db.execute('SELECT * FROM producto WHERE id = ?', (4,)).fetchone()
    return  render_template('comprar.html',producto=producto)

@app.route('/log_out')
def log_out():
    session.clear()
    return redirect(url_for('log_in'))

@app.route('/nuevoproducto', methods=["GET", "POST"])
@login_required
def  nuevoproducto():
    if g.user[6]=='usuario':
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No se ha seleccionado un archivo')
            return render_template('nuevoproducto.html')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No se ha seleccionado un archivo')
            return render_template('nuevoproducto.html')
        if file and allowed_file(file.filename):
            name= request.form['nombre']
            descripcion=request.form['descripcion']
            precio = request.form['precio']
            error = None
            db = get_db()
            if not name:
                error = 'Debe ingresar un nombre de producto'
                flash( error )
            if not precio:
                error = 'Debe ingresar un precio del producto'
                flash( error )
            if not descripcion:
                error = 'Debe ingresar una descripción del producto'
                flash( error )

            if error is not None:
                return render_template('nuevoproducto.html')
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute(
                    'INSERT INTO producto (nombre, descripcion, precio, imagen) VALUES (?,?,?,?)',
                    (name,descripcion, precio, os.path.join(app.config['UPLOAD_FOLDER'], filename) )
                )
                db.commit()
                return render_template('nuevoproducto.html')
        else:
            error = 'Debe cargar un archivo .png'
            flash( error )
            return render_template('nuevoproducto.html')

    return  render_template('nuevoproducto.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/adminusuarios', methods=["GET", "POST"])
@login_required
def  adminusuarios():
    if g.user[6]=='usuario':
        return redirect(url_for('inicio'))
    elif g.user[6]=='superadministrador':
        db=get_db()
        usuarios=db.execute(
            'SELECT * FROM usuario'
        ).fetchall()
    else:
        db=get_db()
        usuarios=db.execute(
            'SELECT * FROM usuario WHERE rol!="superadministrador"'
        ).fetchall()
    
    if request.method=="POST":
        usuario=request.form["usuario"]
        campo=request.form["campo"]
        valor=request.form["valor"]
        if not usuario:
            error = 'Debes elegir un usuario'
            flash( error )
            return render_template('admin.html',usuarios=usuarios)
        if not campo:
            error = 'Debes ingresar un campo a modificar'
            flash( error )
            return render_template('admin.html',usuarios=usuarios)
        if not campo:
            error = 'Debes ingresar la información que se va a cambiar'
            flash( error )
            return render_template('admin.html',usuarios=usuarios)
        if campo=="Nombre y Apellido":
            db.execute(
                    'UPDATE usuario SET nombre=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()

        elif campo=="Telefono":
            db.execute(
                    'UPDATE usuario SET telefono=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()
        
        elif campo=="Correo":
            db.execute(
                    'UPDATE usuario SET correo=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()

        elif campo=="contraseña":
            db.execute(
                    'UPDATE usuario SET contrasena=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()

        elif campo=="¿Recibe promociones?":
            db.execute(
                    'UPDATE usuario SET promo=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()

        elif campo=="Rol":
            db.execute(
                    'UPDATE usuario SET rol=? WHERE id=?',
                    (valor, usuario)
            )
            db.commit()
        
        if g.user[6]=='superadministrador':
            db=get_db()
            usuarios=db.execute(
                'SELECT * FROM usuario'
            ).fetchall()
        else:
            db=get_db()
            usuarios=db.execute(
                'SELECT * FROM usuario WHERE rol!="superadministrador"'
            ).fetchall()

        return render_template('admin.html',usuarios=usuarios)
    return render_template('admin.html',usuarios=usuarios)

if __name__ == '__main__':
    app.run()