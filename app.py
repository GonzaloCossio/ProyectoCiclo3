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

@app.route('/nuevoproducto', methods=["GET"])
def  nuevoproducto(): 
    return  render_template('nuevoproducto.html')