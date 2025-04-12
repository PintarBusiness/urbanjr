from flask import Flask, render_template, request, redirect, url_for, jsonify,session
from flask_session import Session
from tinydb import TinyDB, Query
import re
import requests
import random
import redis
import os
#import requests

# ---------- NALOZI  ----------

#pip install flask --user
#pip install redis
#pip install tinydb

app = Flask(__name__)

# ---------- Funkcije  za admin Session ----------
app.secret_key = os.urandom(24)


app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False

@app.before_request
def make_session_non_permanent():
    session.permanent = False

@app.before_request
def initialize_admin_mode():
    if 'admin_mode' not in session:
        session['admin_mode'] = False
        session['last_log_link'] = "/"

# ---------- Databaze ----------
narocnikiDB = TinyDB('db.json')

# ---------- Linki (poti) do html datotek ----------
@app.route("/")
def index():
    admin_mode = session.get('admin_mode', False)
    return render_template("index.html",admin_mode=admin_mode)

@app.route("/onas")
def onas():
    admin_mode = session.get('admin_mode', False)
    return render_template("onas.html",admin_mode=admin_mode)

@app.route("/trgovina")
def trgovina():
    admin_mode = session.get('admin_mode', False)
    return render_template("trgovina.html",admin_mode=admin_mode)
"""
@app.route("/blog")
def blog():
    admin_mode = session.get('admin_mode', False)
    return render_template("blog.html",admin_mode=admin_mode)
"""
@app.route("/kontakt")
def kontakt():
    admin_mode = session.get('admin_mode', False)
    return render_template("kontakt.html",admin_mode=admin_mode)

@app.route("/admin")
def admin():
    referring_url = request.referrer or "/"  
    session['last_log_link'] = referring_url
    return render_template("admin.html")

@app.route("/logout")
def logout():
    referring_url = request.referrer or "/" 
    session['last_log_link'] = referring_url
    return render_template("logout.html")

@app.route("/narocila")
def narocila():
    admin_mode = session.get('admin_mode', False)
    return render_template("narocila.html",admin_mode=admin_mode)

# ---------- Prijava v admin ----------

userDict = {}
passwordDict = {}

userDict["admin"] = 1
passwordDict["admin"] = 1

@app.route("/loginTry", methods=["POST"])
def login():
    ime = request.form.get("ime") 
    geslo = request.form.get("geslo")  

    if ime in userDict and geslo in passwordDict:
        if userDict[ime] == passwordDict[geslo]:
            session['admin_mode'] = True
            return jsonify({"redirect_to": session['last_log_link']})  
        else:
            return jsonify({"error": "Vnešeno ime ali geslo je napačno"}), 400
    else:
        return jsonify({"error": "Vnešeno ime ali geslo je napačno"}), 400

# ---------- Odjava iz admina ----------

@app.route("/logoutSession", methods=["POST"])
def logoutSession():
    session['admin_mode'] = False
    return jsonify({"redirect_to": session['last_log_link']}) 

@app.route("/goBack", methods=["POST"])
def goBack():
    return jsonify({"redirect_to": session['last_log_link']})  

# ---------- Dodajanje e-mail racuna v databazo TinyDB (za novice) ----------

@app.route("/poskusDodajanjaMail", methods=["POST"])
def poskusDodajanjaMail():
    mail = request.form.get("mail")
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    mailTest = re.match(pattern, mail) is not None
    if (mailTest):
        User = Query()
        if len(narocnikiDB.search(User.mail == mail))==0:
            narocnikiDB.insert({"mail":mail})
        return jsonify(success=True)
    else:
        return jsonify(success=False)

# ---------- Delovanje kosarice ----------

izdelek_podatki = {
    "JAJCA": {
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>JAJCA</h1>
                <a href="/odstrani_iz_kosarice/JAJCA" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07972-20.JPG" alt="Jajca">
            </div>
        </div>
        '''
    },
    "PIŠČANCI": {
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>PIŠČANCI</h1>
                <a href="/odstrani_iz_kosarice/PIŠČANCI" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07979-21.JPG" alt="Piščanci">
            </div>
        </div>
        '''
    },
    "MLEKO": {
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>MLEKO</h1>
                <a href="/odstrani_iz_kosarice/MLEKO" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC08006-26.JPG" alt="Mleko">
            </div>
        </div>
        '''
    },
    "ZELENJAVA": {
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>ZELENJAVA</h1>
                <a href="/odstrani_iz_kosarice/ZELENJAVA" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07972-20.JPG" alt="Zelenjava">
            </div>
        </div>
        '''
    },
    "GOVEDINA": {
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>GOVEDINA</h1>
                <a href="/odstrani_iz_kosarice/GOVEDINA" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07979-21.JPG" alt="Govedina">
            </div>
        </div>
        '''
    }
}

@app.route("/dodaj_v_kosarico/<izdelek>")
def dodaj_v_kosarico(izdelek):
    kosarica = session.get("kosarica", [])
    if izdelek.upper() not in kosarica:
        kosarica.append(izdelek.upper())
    session["kosarica"] = kosarica
    return redirect(url_for("kosarica"))

@app.route("/odstrani_iz_kosarice/<izdelek>")
def odstrani_iz_kosarice(izdelek):
    kosarica = session.get("kosarica", [])
    izdelek_upper = izdelek.upper()
    if izdelek_upper in kosarica:
        kosarica.remove(izdelek_upper)
    session["kosarica"] = kosarica
    return redirect(url_for("kosarica"))

@app.route("/kosarica")
def kosarica():
    admin_mode = session.get('admin_mode', False)
    izbrani_izdelki_imena = session.get("kosarica", [])

    izbrani = []
    neizbrani = []

    for ime, podatki in izdelek_podatki.items():
        html = podatki["html"]
        if ime in izbrani_izdelki_imena:
            izbrani.append(html)
        else:
            html_zamenjan = html.replace(
                f"/odstrani_iz_kosarice/{ime}", f"/dodaj_v_kosarico/{ime}"
            ).replace("ODSTRANI IZDELEK", "DODAJ&nbsp;IZDELEK")
            neizbrani.append(html_zamenjan)

    return render_template("kosarica.html", izbrani=izbrani, neizbrani=neizbrani ,admin_mode=admin_mode)

igtoken = ""
iguporabnik = ""
igapi = ""

def instagramapi():
    objave = {
        "fields": "id,caption,media_type,media_url,permalink",
        "access_token": igtoken,
        "limit": 6
    }

    odgovor = requests.get(igapi, params=objave)
    return odgovor.json().get("data", [])

@app.route("/blog")

def blog():
    poslji = instagramapi
    admin_mode = session.get('admin_mode', False)
    return render_template("blog.html", post=poslji,admin_mode=admin_mode)

@app.route("/api/poslji")

def apiposlji():
    poslji = instagramapi
    return jsonify(poslji)

app.run(debug = True)


