from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_session import Session
from flask_mail import Mail, Message
from tinydb import TinyDB, Query
from dotenv import load_dotenv
import re
import requests
import random
import redis
import os
import smtplib
import datetime
#import requests

# ---------- NALOZI  ----------

#pip install flask --user
#pip install redis
#pip install tinydb

# Load environment variables first
load_dotenv() 

app = Flask(__name__)


# ---------- Pridobitev podatkov iz .env ----------
app.secret_key = os.environ['SECRET_KEY'] 
MAIL_SERVER=os.getenv('MAIL_SERVER'),
MAIL_PORT=int(os.getenv('MAIL_PORT')),
MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')

#  ---------- Zagon potreben za pošiljanje mail ----------
mail = Mail(app)


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
    admin_mode = session.get("admin_mode", False)
    return render_template("trgovina.html", zaloga=pridobi_zalogo(), admin_mode=admin_mode)

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

@app.route("/pomoc")
def pomoc():
    admin_mode = session.get('admin_mode', False)
    return render_template("pomoc.html",admin_mode=admin_mode)

# ---------- Prijava v admin ----------

userDict = {}
passwordDict = {}

AdminName = app.secret_key = os.environ['ADMIN_NAME'] 
AdminPassword = app.secret_key = os.environ['ADMIN_PASSWORD']

userDict[AdminName] = 1
passwordDict[AdminPassword] = 1

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
    print("heh")
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    mailTest = re.match(pattern, mail) is not None
    if (mailTest):
        User = Query()
        if len(narocnikiDB.search(User.mail == mail))==0:
            narocnikiDB.insert({"mail":mail})
        return jsonify(success=True)
    else:
        return jsonify(success=False)

# ---------- INSTAGRAM API  ----------
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
                <p>V vsakem paketu je 10 jajc</p>
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
                <p>V vsakem paketu je 10 jajc</p>
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
                <p>V vsakem paketu je 10 jajc</p>
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
                <p>V vsakem paketu je 10 jajc</p>
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
    izdelek_upper = izdelek.upper()

    # Pridobi pravo zalogo iz baze
    trenutna_zaloga = pridobi_zalogo()
    na_voljo = trenutna_zaloga.get(izdelek_upper, 0)
    v_kosarici = kosarica.get(izdelek_upper, 0)

    if v_kosarici < na_voljo:
        kosarica[izdelek_upper] = v_kosarici + 1
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

# Za naročila v bazo

db_narocila = TinyDB("naročila.json")

@app.route("/oddaj_narocilo", methods=["POST"])
def oddaj_narocilo():
    admin_mode = session.get('admin_mode', False)
    session["zaloga"] = pridobi_zalogo()
    zahtevani_podatki = ["ime", "priimek", "telefonska", "e-pošta", "kraj", "hisnastevilka", "poštnaštevilka", "nacindostave"]
    manjkajoci = [p for p in zahtevani_podatki if not request.form.get(p)]
    if manjkajoci:
        return redirect(url_for("kosarica"))

    kosarica = session.get("kosarica", {})
    zaloga = session.get("zaloga", {})

    # Shrani naročilo v bazo
    narocilo = {
        "ime": request.form["ime"],
        "priimek": request.form["priimek"],
        "telefonska": request.form["telefonska"],
        "eposta": request.form["e-pošta"],
        "kraj": request.form["kraj"],
        "hisna_stevilka": request.form["hisnastevilka"],
        "postna_stevilka": request.form["poštnaštevilka"],
        "nacin_dostave": request.form["nacindostave"],
        "izdelki": kosarica,
        "datum": datetime.now().strftime("%d.%m.%Y ob %H:%M")
    }

    db_narocila.insert(narocilo)

    # Posodobi zalogo
    for izdelek, kolicina in kosarica.items():
        obstojece = zalogaDB.get(ZalogaQuery.izdelek == izdelek)
        if obstojece:
            nova_kolicina = max(0, obstojece["kolicina"] - kolicina)
            zalogaDB.update({"kolicina": nova_kolicina}, ZalogaQuery.izdelek == izdelek)

    session["zaloga"] = zaloga
    session["kosarica"] = {}

    return render_template("hvala.html", admin_mode=admin_mode)

@app.route("/kosarica")
def kosarica():
    kosarica_ses = session.get("kosarica", {})
    admin_mode = session.get('admin_mode', False)
    trenutna_zaloga = pridobi_zalogo()  # <-- Ključno

    izbrani = []
    neizbrani = []

    for ime, podatki in izdelek_podatki.items():
        html = podatki["html"]
        if ime in kosarica_ses:
            kolicina = kosarica_ses[ime]
            zaloga_kolicina = trenutna_zaloga.get(ime, 0)

            # Gumb za +
            if kolicina >= zaloga_kolicina:
                povecaj_gumb = f'<span class="stevecgumb onemogoceno">+</span>'
            else:
                povecaj_gumb = f'<a href="/povecaj/{ime}" class="stevecgumb">+</a>'

            html += f'''
                <div class="stevec">
                    <a href="/znizaj/{ime}" class="stevecgumb">-</a>
                    <span class="steveckolicina">{kolicina}</span>
                    {povecaj_gumb}
                </div>
            '''
            izbrani.append(html)
        else:
            zaloga_kolicina = trenutna_zaloga.get(ime, 0)

            if zaloga_kolicina > 0:
                html_zamenjan = html.replace(
                    f"/odstrani_iz_kosarice/{ime}", f"/dodaj_v_kosarico/{ime}"
                ).replace("ODSTRANI IZDELEK", "DODAJ&nbsp;IZDELEK")
            else:
                html_zamenjan = html.replace(
                    f"/odstrani_iz_kosarice/{ime}", "#"
                ).replace("ODSTRANI IZDELEK", "NI&nbsp;NA&nbsp;VOLJO")

            neizbrani.append(html_zamenjan)

    return render_template("kosarica.html", izbrani=izbrani, neizbrani=neizbrani, admin_mode=admin_mode, zaloga=trenutna_zaloga)

# ---------- Delovanje pregled zaloge ----------

zalogaDB = TinyDB("zaloga.json")
ZalogaQuery = Query()

@app.route("/pregled")
def pregled():
    narocila = db_narocila.all()

    def parse_datum(n):
        try:
            return datetime.strptime(n["datum"], "%d.%m.%Y ob %H:%M")
        except:
            return datetime.min  # če je kaj narobe z datumom

    narocila = sorted(narocila, key=parse_datum, reverse=True)

    narocila = narocila[:30]
    maili = narocnikiDB.all()
    zaloga = pridobi_zalogo()
    admin_mode = session.get('admin_mode', False)
    return render_template("pregled.html", narocila=narocila, zaloga=zaloga, maili=maili, admin_mode=admin_mode)

@app.route("/nastavi_zalogo", methods=["POST"])
def nastavi_zalogo():
    for izdelek in izdelek_podatki.keys():
        kolicina = int(request.form.get(izdelek, "0") or 0)
        if zalogaDB.contains(ZalogaQuery.izdelek == izdelek):
            zalogaDB.update({"kolicina": kolicina}, ZalogaQuery.izdelek == izdelek)
        else:
            zalogaDB.insert({"izdelek": izdelek, "kolicina": kolicina})
    return redirect(url_for("pregled"))

def pridobi_zalogo():
    podatki = zalogaDB.all()
    return {item["izdelek"]: item["kolicina"] for item in podatki}

# ---------- Kontakt pošiljanje na mail ----------

@app.route('/posljiPriporocilo', methods=['POST'])
def posljiPriporocilo():
    # Podatki iz html
    name = request.form.get('ime_posiljatelj')
    sender_email = request.form.get('mail_posiljatelj')
    message = request.form.get('sporocilo_posiljatelj')

    # povezava mail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = os.getenv('MAIL_USERNAME')  
    password = os.getenv('MAIL_PASSWORD')  
    recipient = os.getenv('MAIL_USERNAME')

    # Mail vsebina
    subject = f"Novo sporočilo od {name} (Urban JR. Kontakt)"
    body = f"""Pošiljatelj: {name}
Email: {sender_email}

Sporočilo:
{message}"""
    # Celotna vsebina mail
    email_message = f"""Subject: {subject}
To: {recipient}
From: {username}
Reply-To: {sender_email}

{body}"""
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() 
            server.login(username, password)
            server.sendmail(username, recipient, email_message.encode('utf-8'))
        
        flash('Sporočilo poslano! Hvala.', 'success')
    except smtplib.SMTPAuthenticationError:
        flash('Napaka pri prijavi. Preverite uporabniško ime in geslo.', 'danger')
        print("SMTP Authentication Error")
    except smtplib.SMTPException as e:
        flash('Napaka pri pošiljanju. Prosimo, poskusite kasneje.', 'danger')
        print(f"SMTP Error: {e}")
    except Exception as e:
        flash('Nepričakovana napaka.', 'danger')
        print(f"General Error: {e}")

    return redirect(url_for('kontakt'))




app.run(debug = True, port=8800)


