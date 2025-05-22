# flask
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_mail import Mail, Message
import requests

# navadno
import os
import html
from datetime import datetime 
import json 	
import traceback

# databaza
from tinydb import TinyDB, Query

# pišiljanje emailov + slovenski znaki v emailih
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.charset import Charset, QP
import smtplib

#iskanje
import re

#tajnost
from dotenv import load_dotenv




# ---------- NALOZI  ----------

#pip install flask --user
#pip install tinydb
# -- pa seveda se kaj drugega :) --

# Load environment variables first
load_dotenv() 

app = Flask(__name__)


# ---------- Pridobitev podatkov iz .env ----------
app.secret_key = os.getenv('SECRET_KEY', 'your_fallback_secret_key_here')
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'jure.pintar9@gmail.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'wnia dkdk zpby hotv')

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

@app.route("/pravno")
def pravno():
    admin_mode = session.get('admin_mode', False)
    return render_template("pravno.html",admin_mode=admin_mode)

# ---------- Prijava v admin ----------

userDict = {}
passwordDict = {}

AdminName = os.getenv('ADMIN_NAME', 'admin')
AdminPassword = os.getenv('ADMIN_PASSWORD', 'securepassword')

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
narocnikiDB = TinyDB('naročniki.json')

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

# ---------- Pošiljanje novic  ----------

noviceDB = TinyDB('novice.json')

# Pot za slike
UPLOAD_FOLDER = os.path.join("static", "images", "novice")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/dodajnovico", methods=["POST"])
def dodajnovico():
    naslov = request.form.get("naslov")
    besedilo = request.form.get("besedilo")
    slika_file = request.files.get("slika")

    slika_ime = ""
    if slika_file:
        slika_ime = slika_file.filename
        slika_path = os.path.join(UPLOAD_FOLDER, slika_ime)
        slika_file.save(slika_path)

    User = Query()
    if len(noviceDB.search(User.naslov == naslov)) == 0:
        noviceDB.insert({
            "naslov": naslov,
            "besedilo": besedilo,
            "slika": slika_ime,
            "cas": datetime.utcnow().isoformat()
        })

    return jsonify(success=True)

@app.route("/odstrani_novico", methods=["POST"])
def odstrani_novico():
    if not session.get('admin_mode'):
        return redirect(url_for("blog"))

    naslov = request.form.get("naslov")
    User = Query()
    noviceDB.remove(User.naslov == naslov)

    return redirect(url_for("blog"))

@app.route("/blog")
def blog():
    admin_mode = session.get('admin_mode', False)
    vse_novice = noviceDB.all()
    # sortiramo po času padajoče, najnovejša prva
    vse_novice_sorted = sorted(vse_novice, key=lambda x: x.get("cas", ""), reverse=True)
    return render_template("blog.html", admin_mode=admin_mode, novice=vse_novice_sorted)

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
            <div class="cena">
                <p>3.5 €</p>
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
            <div class="cena">
                <p>14 €</p>
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
            <div class="cena">
                <p>2 €</p>
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
            <div class="cena">
                <p>5 €</p>
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
                <p>V vsakem paketu je 0.5 kg govedine</p>
            </div>
            <div class="cena">
                <p>20 €</p>
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

def izracunaj_skupno_ceno(kosarica_ses):
    skupna = 0.0
    for ime, kolicina in kosarica_ses.items():
        podatki = izdelek_podatki.get(ime.upper())
        if podatki:
            html = podatki["html"]
            # Poišči prvo ceno v HTML
            match = re.search(r'(\d+(?:\.\d+)?)\s*€', html)
            if match:
                cena = float(match.group(1))
                skupna += cena * kolicina
    return round(skupna, 2)



# ---------- Za pošiljanje e-maila ob nakupu ----------
import html

def html_narocilo(ime, priimek, telefonska, sender_email, kraj, hisna_stevilka, postna_stevilka, nacin_dostave, izdelki, datum, skupna_cena):
    # Pretvorba izdelkov, da se uporabi HTML escape in nadomesti \n z <br>
    izdelki_html = html.escape(izdelki).replace('\n', '<br>')

    html_narocilo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 0.7;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #B4B436;
                color: white;
                padding: 0.5em;
                font-size: 1.6em;
                text-align: center;
                border-radius: 1.5em;
                width:88%;
            }}
            .content {{
                padding: 1.5em;
                background-color: #f9f9f9;
                border: 0.15em solid #ddd;
                margin-top: 1em;
                border-radius: 2em;
                width: 85%
            }}
            .content p {{
                line-height: 1.1;
                color: #DBBB92;
                font-size: 0.9em;
                margin-left: 0.5em;
            }}
            table {{
                width: 90%;
                margin: auto;
            }}
            .prostor {{
                width: 45%;
            }}
            .presledek {{
                width: 10%;
            }}
            .imemail {{
                border-radius: 1em;
                background-color: white;
                border: 0.3em solid #DBBB92;
                width: 100%;
            }}
            .izdelki {{
                font-size: 1.3em;
                margin: 0.8em;
                color: #DBBB92;
            }}
            strong {{
                font-family: sans-serif;
                font-size: 1.6em;
                color: #B4B436;
            }}
            .footer {{
                width: 100%;
                text-align: center;
                font-size: 0.9em;
            }}
            .pomemben_text {{
                font-size: 2.8em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Naročilo iz spletne strani Urban JR.</h2>
        </div>
        <div class="content">
            <table>
                <tr>
                    <td><p><strong>Ime:</strong></p></td>
                    <td>&nbsp;&nbsp;</td>
                    <td><p><strong>Priimek:</strong></p></td>
                </tr>
                <tr>
                    <td class="prostor">
                        <div class="imemail">
                            <p>{html.escape(ime)}</p>
                        </div><br>
                    </td>
                    <td>&nbsp;&nbsp;</td>
                    <td class="prostor">
                        <div class="imemail">
                            <p>{html.escape(priimek)}</p>
                        </div><br>
                    </td>
                </tr>
                <tr>
                    <td><p><strong>Telefonska številka:</strong></p></td>
                    <td>&nbsp;&nbsp;</td>
                    <td><p><strong>e-mail:</strong></p></td>
                </tr>
                <tr>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(telefonska)}</p>
                        </div><br>
                    </td>
                    <td class="presledek">&nbsp;&nbsp;</td>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(sender_email)}</p>
                        </div><br>
                    </td>
                </tr>
                <tr>
                    <td><p><strong>Kraj:</strong></p></td>
                    <td>&nbsp;&nbsp;</td>
                    <td><p><strong>Hišna številka:</strong></p></td>
                </tr>
                <tr>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(kraj)}</p>
                        </div><br>
                    </td>
                    <td>&nbsp;&nbsp;</td>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(hisna_stevilka)}</p>
                        </div><br>
                    </td>
                </tr>
                <tr>
                    <td><p><strong>Poštna številka:</strong></p></td>
                    <td>&nbsp;&nbsp;</td>
                    <td><p><strong>Način dostave:</strong></p></td>
                </tr>
                <tr>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(postna_stevilka)}</p>
                        </div><br>
                    </td>
                    <td>&nbsp;&nbsp;</td>
                    <td>
                        <div class="imemail">
                            <p>{html.escape(nacin_dostave)}</p>
                        </div><br>
                    </td>
                </tr>
                <tr>
                    <td colspan="3">
                        <p><strong class="pomemben_text">Naročeni izdelki:</strong></p>
                        <div class="imemail">
                            <div class="izdelki">{izdelki_html}</div>
                        </div><br>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p><strong>Datum:</strong></p>
                    </td>
                    <td>&nbsp;&nbsp;</td>
                    <td>
                        <p><strong>Skupna cena:</strong></p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="imemail">
                        <p>{html.escape(datum)}</p>
                        </div><br>
                    </td>
                    <td>&nbsp;&nbsp;</td>
                    <td>
                        <div class="imemail">
                            <div class="izdelki">{html.escape(str(skupna_cena))} €</div>
                        </div><br>
                    </td>
                </tr>
            </table>  
        </div>
        <div class="footer">
            <p>Nakup uporabnika iz strani Urban JR.</p>
        </div>
    </body>
    </html>
    """
    return html_narocilo


def narocilo_poslji_mail(narocilo):
    try:
        # slovenski znaki
        charset = Charset('utf-8')
        charset.body_encoding = QP  
        charset.header_encoding = QP
        def ensure_unicode(s):
            if isinstance(s, bytes):
                return s.decode('utf-8', errors='replace')
            return str(s)
        data = {k: ensure_unicode(v) for k, v in narocilo.items()}

        # server mail
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        recipient = os.getenv('MAIL_USERNAME')

        # ustvarjanje sporočila na emailu
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf-8')
        msg['Subject'] = Header(
            f"Naročilo osebe: {data['ime']} {data['priimek']}",
            'utf-8'
        )
        msg['From'] = Header(f"Urban JR <{username}>", 'utf-8')
        msg['To'] = recipient
        msg['Reply-To'] = data['eposta']

        # omogočanje slovenskih simbolov
        def safe_content(s):
            try:
                return html.escape(ensure_unicode(s))
            except:
                return str(s) 
        strIzdelkov = ""
        for key, value in json.loads(data["izdelki"].replace("'",'"')).items():
            strIzdelkov += f"{value}X {key} \n"
        print(strIzdelkov)

        # klic izdelava html
        narocilo_html_content = html_narocilo(
            safe_content(data['ime']), safe_content(data['priimek']),
            safe_content(data['telefonska']), safe_content(data['eposta']),
            safe_content(data['kraj']), safe_content(data['hisna_stevilka']),
            safe_content(data['postna_stevilka']), safe_content(data['nacin_dostave']),
            safe_content(strIzdelkov), safe_content(data['datum']),
            safe_content(data['skupna_cena'])
        )
        # navadni text
        narocilo_text_content = f"""Naročilo:
Ime: {data['ime']}
Priimek: {data['priimek']}
Telefon: {data['telefonska']}
Email: {data['eposta']}
Kraj: {data['kraj']}
Hišna številka: {data['hisna_stevilka']}
Poštna številka: {data['postna_stevilka']}
Način dostave: {data['nacin_dostave']}
Izdelki: {data['izdelki']}
Datum: {data['datum']}
Skupna cena: {data['skupna_cena']} €"""

        # poti MIME za email
        part1 = MIMEText(narocilo_text_content, 'plain', 'utf-8')
        part1.set_charset('utf-8')
        
        part2 = MIMEText(narocilo_html_content, 'html', 'utf-8')
        part2.set_charset('utf-8')
        
        msg.attach(part1)
        msg.attach(part2)

        # pošiljanje email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            raw_message = msg.as_string()
            if isinstance(raw_message, str):
                raw_message = raw_message.encode('utf-8')
            server.sendmail(username, recipient, raw_message)
        flash('Sporočilo poslano! Hvala.', 'success')
    except Exception as e:
        error_msg = f'Napaka pri pošiljanju: {str(e)}'
        if 'ascii' in str(e).lower():
            error_msg = 'Napaka pri kodiranju znakov (č, š, ž). Prosimo, poskusite znova.'
        flash(error_msg, 'danger')
        print(f"Error details: {repr(e)}")

# ---------- Kosarica ----------
@app.route("/kosarica")
def kosarica():
    kosarica_ses = session.get("kosarica", {})
    admin_mode = session.get('admin_mode', False)
    skupna_cena = izracunaj_skupno_ceno(kosarica_ses)
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

    return render_template("kosarica.html", izbrani=izbrani, neizbrani=neizbrani, admin_mode=admin_mode, zaloga=trenutna_zaloga, skupna_cena=skupna_cena)

# ---------- funkcija za oddajo naročila v košarici ----------
@app.route("/oddaj_narocilo", methods=["POST"])
def oddaj_narocilo():
    admin_mode = session.get('admin_mode', False)
    session["zaloga"] = pridobi_zalogo()
    zahtevani_podatki = ["ime", "priimek", "telefonska", "e-pošta", "kraj", "hisnastevilka", "poštnaštevilka", "nacindostave"]
    manjkajoci = [p for p in zahtevani_podatki if not request.form.get(p)]
    if manjkajoci:
        return redirect(url_for("kosarica"))

    kosarica = session.get("kosarica", {})
    skupna_cena = izracunaj_skupno_ceno(kosarica)
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
        "datum": datetime.now().strftime("%d.%m.%Y ob %H:%M"),
        "skupna_cena": skupna_cena
    }

    db_narocila.insert(narocilo)
    narocilo_poslji_mail(narocilo)

    # Posodobi zalogo
    for izdelek, kolicina in kosarica.items():
        obstojece = zalogaDB.get(ZalogaQuery.izdelek == izdelek)
        if obstojece:
            nova_kolicina = max(0, obstojece["kolicina"] - kolicina)
            zalogaDB.update({"kolicina": nova_kolicina}, ZalogaQuery.izdelek == izdelek)

    session["zaloga"] = zaloga
    session["kosarica"] = {}

    return render_template("hvala.html", admin_mode=admin_mode, skupna_cena=skupna_cena)


# ---------- Delovanje pregled zaloge ----------

zalogaDB = TinyDB("zaloga.json")
ZalogaQuery = Query()
# Za naročila v bazo

db_narocila = TinyDB("naročila.json")

@app.route("/pregled")
def pregled():
    if not session.get('admin_mode', False):
        return redirect("/")
    try:
        narocila = db_narocila.all()

        narocniki_text = ""
        for entry in narocnikiDB.all():
            narocniki_text += entry['mail'] +","
        narocniki_text = narocniki_text[:-1]

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
        return render_template("pregled.html", narocila=narocila, zaloga=zaloga, maili=maili, narocniki_text=narocniki_text,admin_mode=admin_mode)
    except Exception as e:
        print("Napaka v /pregled:", e)
        traceback.print_exc()
        return "Napaka na strežniku", 500

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


def html_kontakt(name, sender_email, message): 
    # Escapiranje podatkov in obdelava nove vrstice v sporočilu
    escaped_name = html.escape(name)
    escaped_sender_email = html.escape(sender_email)
    escaped_message = html.escape(message).replace("\n", "<br>")  # Pretvori nove vrstice v <br> za HTML

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{
                display: flex;
                justify-content:center;
                align-items:center;
                font-family: 'Arial', sans-serif;
                line-height: 1.2;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #B4B436;
                color: white;
                padding: 0.5em;
                font-size: 1.6em;
                text-align: center;
                border-radius: 1.5em;
                width:88%;
            }}
            .content {{
                padding: 1.5em;
                background-color: #f9f9f9;
                border: 0.15em solid #ddd;
                margin-top: 1em;
                border-radius: 2em;
                width: 85%;
            }}
            .content p {{
                line-height: 1.2;
                color: #DBBB92;
                font-size: 1.2em;
                margin-left: 1em;
            }}
            .message {{
                background-color: white;
                padding: 1.5em;
                padding-top: 0;
                color: #DBBB92;
                border: 0.3em solid #DBBB92;
                border-radius: 1.5em;
                font-size:1.1em;
                height: 20em;
                width: 84%;
                overflow-y: auto;
                overflow-x: hidden;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .imemail {{
                border-radius: 1em;
                background-color: white;
                border: 0.3em solid #DBBB92;
                width: 30%;
                min-width:20em;
            }}
            strong {{
                font-family: sans-serif;
                font-size: 1.7em;
                color: #B4B436;
            }}
            .footer {{
                width:100%;
                text-align: center;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Vprašanje iz spletne strani Urban JR.</h2>
        </div>
        <div class="content">
            <p><strong>Ime:</strong></p>
            <div class="imemail">
                <p>{escaped_name}</p>
            </div><br>
            <p><strong>e-mail:</strong></p>
            <div class="imemail">
                <p>{escaped_sender_email}</p>
            </div><br>
            <p><strong>Vprašanje:</strong></p>
            <div class="message">
                {escaped_message}
            </div>
        </div>
        <div class="footer">
            <p>Vprašanje uporabnika iz kontaktnega obrazca na spletni strani Urban JR.</p>
        </div>
    </body>
    </html>
    """
    return html_content


@app.route('/posljiPriporocilo', methods=['POST'])
def posljiPriporocilo():
    try:
        # slovenski znaki
        charset = Charset('utf-8')
        charset.body_encoding = QP
        charset.header_encoding = QP
        def ensure_unicode(s):
            if isinstance(s, bytes):
                return s.decode('utf-8', errors='replace')
            return str(s)

        # podatki
        name = ensure_unicode(request.form.get('ime_posiljatelj', ''))
        sender_email = ensure_unicode(request.form.get('mail_posiljatelj', ''))
        message = ensure_unicode(request.form.get('sporocilo_posiljatelj', ''))

        # email server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        recipient = os.getenv('MAIL_USERNAME')

        # ustvarjanje email sporočila
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf-8')
        msg['Subject'] = Header(f"Vprašanje od osebe: {name}", 'utf-8')
        msg['From'] = Header(f"Urban JR <{username}>", 'utf-8')
        msg['To'] = recipient
        msg['Reply-To'] = sender_email
        def safe_content(content):
            try:
                return html.escape(content)
            except:
                return str(content)

        # klic izdelava html
        kontakt_html_content = html_kontakt(
            safe_content(name),
            safe_content(sender_email),
            safe_content(message)
        )

        # navadni text
        kontakt_text_content = f"""Vprašanje od stranke:
Ime: {name}
Email: {sender_email}
Sporočilo:
{message}"""

        # uporaba MIME za izdelavo emaila
        part1 = MIMEText(kontakt_text_content, 'plain', 'utf-8')
        part1.set_charset('utf-8')
        
        part2 = MIMEText(kontakt_html_content, 'html', 'utf-8')
        part2.set_charset('utf-8')
        
        msg.attach(part1)
        msg.attach(part2)

        # pošiljanje emaila
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            raw_message = msg.as_string()
            if isinstance(raw_message, str):
                raw_message = raw_message.encode('utf-8')
            server.sendmail(username, recipient, raw_message)
        flash('Sporočilo poslano! Hvala.', 'success')
    except Exception as e:
        error_msg = f'Napaka pri pošiljanju: {str(e)}'
        if 'ascii' in str(e).lower():
            error_msg = 'Napaka pri kodiranju znakov (č, š, ž). Prosimo, poskusite znova.'
        flash(error_msg, 'danger')
        print(f"Error details: {repr(e)}")

    return redirect(url_for('kontakt'))




app.run(debug = True, port=8800)


