from flask import Flask, render_template
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

app.run(debug = True)


"""
we have our website uploaded on github. our link is https://pintarbusiness.github.io/urbanjr/ . The link worked as long as we did not make the right structure. When index.html was outside the templates folder it worked but when we placed it into te folder it sttoped working
"""