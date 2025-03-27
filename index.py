from flask import Flask, render_template
import random
#import requests

#pip install flask --user

app = Flask(__name__)


@app.route("/")

def api_poskus():
    print("skoz")
    return render_template("index.html")

app.run(debug = True)