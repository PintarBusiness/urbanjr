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
    izbrani_izdelki_imena = session.get("kosarica", [])
    izbrani = [izdelek_podatki.get(ime) for ime in izbrani_izdelki_imena if ime in izdelek_podatki]
    return render_template("kosarica.html", izbrani=izbrani)


app.run(debug = True, port=8800)


