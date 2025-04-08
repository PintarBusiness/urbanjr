from flask import Flask, render_template, request
import requests
import random
#import requests

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

@app.route("/blog")

def blog():
    return render_template("blog.html")

@app.route("/kontakt")

def kontakt():
    return render_template("kontakt.html")

@app.route("/admin")

def admin():
    return render_template("admin.html")

@app.route("/narocila")
def narocila():
    return render_template("narocila.html")

userDict = {}
passwordDict = {}

userDict["jure"] = 1
passwordDict["pintar"] = 1

@app.route("/loginTry")
def login():
    ime = request.args.get("ime")
    geslo = request.args.get("geslo")

    if ime in userDict and geslo in passwordDict:
        if userDict[ime] == passwordDict[geslo]:
            return f"{ime} {geslo}"
        else:
            return f"Vnešeno ime ali geslo je napačno"
    else:
        return f"Vnešeno ime ali geslo je napačno"
app.run(debug = True, port=8800)


