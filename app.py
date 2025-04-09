from flask import Flask, render_template, jsonify
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


@app.route("/kontakt")

def kontakt():
    return render_template("kontakt.html")

@app.route("/admin")

def admin():
    return render_template("admin.html")

@app.route("/kosarica")
def narocila():
    return render_template("kosarica.html")

app.run(debug = True, port=5000)


