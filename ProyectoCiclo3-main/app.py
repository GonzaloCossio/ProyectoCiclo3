import os
from flask import Flask, render_template, flash, request, redirect, url_for

app=Flask(__name__)

app.secret_key = os.urandom(24)

@app.route('/log_in',methods=["GET","POST"])
@app.route('/',methods=["GET","POST"])
def  log_in(): 
    return  render_template('log_in.html')

@app.route('/register',methods=["GET","POST"])
def  register(): 
    return  render_template('register.html')

@app.route('/inicio', methods=["GET","POST"])
def  inicio(): 
    return  "esta es la pantalla de inicio"

@app.route('/producto', methods=["GET", "POST", "DELETE"])
def  producto(): 
    return  render_template('producto.html')

@app.route('/nuevoproducto', methods=["GET", "DELETE"])
def  nuevoproducto(): 
    return  render_template('nuevoproducto.html')

@app.route('/agregar_o_eliminar_producto', methods=["GET", "POST", "DELETE"])
def  agregar_o_eliminar_producto(): 
    return  render_template('agregar_o_eliminar_producto.html')

@app.route('/calificarproducto', methods=["GET", "POST"])
def  calificarproducto(): 
    return  render_template('calificarproducto.html')

@app.route('/wishlist', methods=["GET", "DELETE"])
def  wishlist(): 
    return  render_template('wishlist.html')