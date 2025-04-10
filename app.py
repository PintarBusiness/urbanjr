from flask import Flask, render_template, request, redirect, url_for, jsonify,session
from flask_session import Session
import requests
import random
import redis
import os

#import requests
#pip install flask --user
#pip install redis

app = Flask(__name__)
app.secret_key = os.urandom(24)


app.config['SESSION_TYPE'] = 'filesystem'  # or 'null'
app.config['SESSION_PERMANENT'] = False

@app.before_request
def make_session_non_permanent():
    session.permanent = False



@app.before_request
def initialize_admin_mode():
    if 'admin_mode' not in session:
        session['admin_mode'] = False


@app.route("/")

def index():
    admin_mode = session.get('admin_mode', False)
    return render_template("index.html",admin_mode=admin_mode)

@app.route("/onas")

def onas():
    return render_template("onas.html")

@app.route("/trgovina")

def trgovina():
    return render_template("trgovina.html")

@app.route("/blog")

def blog():
    return render_template("blog.html")

@app.route("/kontakt")

def kontakt():
    return render_template("kontakt.html")

@app.route("/admin")

def admin():
    return render_template("admin.html")

@app.route("/logout")

def logout():
    return render_template("logout.html")

@app.route("/narocila")
def narocila():
    return render_template("narocila.html")

userDict = {}
passwordDict = {}

userDict["admin"] = 1
passwordDict["admin"] = 1

@app.route("/loginTry", methods=["POST"])
def login():
    ime = request.form.get("ime")  # Get 'ime' from the POST request
    geslo = request.form.get("geslo")  # Get 'geslo' from the POST request

    if ime in userDict and geslo in passwordDict:
        if userDict[ime] == passwordDict[geslo]:
            session['admin_mode'] = True
            return jsonify({"redirect_to": "/"})  # URL to redirect to
        else:
            return jsonify({"error": "Vnešeno ime ali geslo je napačno"}), 400
    else:
        return jsonify({"error": "Vnešeno ime ali geslo je napačno"}), 400
    
@app.route("/logoutSession", methods=["POST"])
def logoutSession():
    session['admin_mode'] = False
    return jsonify({"redirect_to": "/"})  # URL to redirect to

app.run(debug = True, port=8800)


