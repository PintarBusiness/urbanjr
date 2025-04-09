from flask import Flask, render_template, jsonify, session, redirect, url_for
import random
import requests

#pip install flask --user

app = Flask(__name__)


@app.route("/")

def index():
    return render_template("index.html")

@app.route("/onas")

def onas():
    return render_template("onas.html")

@app.route("/kontakt")

def kontakt():
    return render_template("kontakt.html")

@app.route("/admin")

def admin():
    return render_template("admin.html")

@app.route("/trgovina")

def trgovina():
    return render_template("trgovina.html")

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
    return render_template("blog.html", post=poslji)

@app.route("/api/poslji")

def apiposlji():
    poslji = instagramapi
    return jsonify(poslji)


app.secret_key = 'skrivnostninkl'

izdelek_podatki = {
    "JAJCA": {
        "naslov": "JAJCA",
        "slika": "static/images/trgovina/DSC07972-20.JPG",
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>JAJCA</h1>
                <a href="/odstrani_iz_kosarice" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07972-20.JPG" alt="Jajca">
            </div>
        </div>
        '''
    },
    "PIŠČANCI": {
        "naslov": "PIŠČANCI",
        "slika": "static/images/trgovina/DSC07979-21.JPG",
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>PIŠČANCI</h1>
                <a href="/odstrani_iz_kosarice" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07979-21.JPG" alt="Piščanci">
            </div>
        </div>
        '''
    },
    "MLEKO": {
        "naslov": "MLEKO",
        "slika": "static/images/trgovina/DSC08006-26.JPG",
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>MLEKO</h1>
                <a href="/odstrani_iz_kosarice" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC08006-26.JPG" alt="Mleko">
            </div>
        </div>
        '''
    },
    "ZELENJAVA": {
        "naslov": "ZELENJAVA",
        "slika": "static/images/trgovina/DSC07972-20.JPG",
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>ZELENJAVA</h1>
                <a href="/odstrani_iz_kosarice" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
            </div>
            <div class="slika">
                <img src="/static/images/trgovina/DSC07972-20.JPG" alt="Zelenjava">
            </div>
        </div>
        '''
    },
    "GOVEDINA": {
        "naslov": "GOVEDINA",
        "slika": "static/images/trgovina/DSC07979-21.JPG",
        "html": '''
        <div class="sliketext">
            <div class="text">
                <h1>GOVEDINA</h1>
                <a href="/odstrani_iz_kosarice" class="gumbnarocila"><span>ODSTRANI IZDELEK</span></a>
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
    
    session["kosarica"] = izdelek.upper()
    return redirect(url_for("kosarica"))

@app.route("/odstrani_iz_kosarice")
def odstrani_iz_kosarice():
    session.pop("kosarica", None)
    return redirect(url_for("kosarica"))

@app.route("/kosarica")
def kosarica():
    izbran_izdelek_ime = session.get("kosarica")
    izbran = izdelek_podatki.get(izbran_izdelek_ime)
    return render_template("kosarica.html", izbran=izbran)

app.run(debug = True, port=5000)


