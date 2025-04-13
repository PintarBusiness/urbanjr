from flask import Flask, render_template, jsonify, session, redirect, url_for, request
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

@app.route("/pomoc")

def pomoc():
    return render_template("pomoc.html")

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
            <div class="opiskoliko">
                <p>V vsakem paketu je 10 jajc</p>
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
            <div class="opiskoliko">
                <p>V vsakem paketu je 1 piščanec</p>
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
            <div class="opiskoliko">
                <p>V vsakem paketu je 1 liter mleka</p>
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
            <div class="opiskoliko">
                <p>Paket mešane zelenjave</p>
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
            <div class="opiskoliko">
                <p>V vsakekem paketu je 0.5 kg govedine</p>
            </div>
        </div>
        '''
    }
}

@app.context_processor
def kosarica_stevec():
    kosarica = session.get("kosarica", {})
    if not isinstance(kosarica, dict):
        kosarica = {}
    skupno = sum(kosarica.values())
    return {"st_izdelkov": skupno}

@app.route("/dodaj_v_kosarico/<izdelek>")
def dodaj_v_kosarico(izdelek):
    kosarica = session.get("kosarica", {})
    if not isinstance(kosarica, dict):
        kosarica = {}
    izdelek_upper = izdelek.upper()
    kosarica[izdelek_upper] = kosarica.get(izdelek_upper, 0) + 1
    session["kosarica"] = kosarica
    return redirect(request.referrer)

@app.route("/odstrani_iz_kosarice/<izdelek>")
def odstrani_iz_kosarice(izdelek):
    kosarica = session.get("kosarica", {})
    if not isinstance(kosarica, dict):
        kosarica = {}
    izdelek_upper = izdelek.upper()
    if izdelek_upper in kosarica:
        del kosarica[izdelek_upper]
    session["kosarica"] = kosarica
    return redirect(url_for("kosarica"))

@app.route("/povecaj/<izdelek>")
def povecaj(izdelek):
    kosarica = session.get("kosarica", {})
    if not isinstance(kosarica, dict):
        kosarica = {}
    izdelek_upper = izdelek.upper()
    if izdelek_upper in kosarica:
        kosarica[izdelek_upper] += 1
    session["kosarica"] = kosarica
    return redirect(url_for("kosarica"))

@app.route("/znizaj/<izdelek>")
def znizaj(izdelek):
    kosarica = session.get("kosarica", {})
    if not isinstance(kosarica, dict):
        kosarica = {}
    izdelek_upper = izdelek.upper()
    if izdelek_upper in kosarica:
        kosarica[izdelek_upper] -= 1
        if kosarica[izdelek_upper] <= 0:
            del kosarica[izdelek_upper]
    session["kosarica"] = kosarica
    return redirect(url_for("kosarica"))

@app.route("/oddaj_narocilo", methods=["POST"])
def oddaj_narocilo():
    zahtevani_podatki = ["ime", "priimek", "telefonska", "e-pošta", "kraj", "hisnastevilka", "poštnaštevilka", "nacindostave"]
    manjkajoci = [p for p in zahtevani_podatki if not request.form.get(p)]
    if manjkajoci:
        return redirect(url_for("kosarica"))
    session["kosarica"] = {}
    return render_template("hvala.html")

@app.route("/kosarica")
def kosarica():
    kosarica_ses = session.get("kosarica", {})

    if not isinstance(kosarica_ses, dict):
        kosarica_ses = {}

    izbrani = []
    neizbrani = []

    for ime, podatki in izdelek_podatki.items():
        html = podatki["html"]
        if ime in kosarica_ses:
            kolicina = kosarica_ses[ime]
            html += f'''
                <div class="stevec">
                    <a href="/znizaj/{ime}" class="stevecgumb">-</a>
                    <span class="steveckolicina">{kolicina}</span>
                    <a href="/povecaj/{ime}" class="stevecgumb">+</a>
                </div>
            '''
            izbrani.append(html)
        else:
            html_zamenjan = html.replace(
                f"/odstrani_iz_kosarice/{ime}", f"/dodaj_v_kosarico/{ime}").replace("ODSTRANI IZDELEK", "DODAJ&nbsp;IZDELEK")
            neizbrani.append(html_zamenjan)

    return render_template("kosarica.html", izbrani=izbrani, neizbrani=neizbrani)
      
app.run(debug = True, port=5000)


