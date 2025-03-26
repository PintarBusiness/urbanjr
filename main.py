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


"""
we have our website uploaded on github. our link is https://pintarbusiness.github.io/urbanjr/ . The link worked as long as we did not make the right structure. When index.html was outside the templates folder it worked but when we placed it into te folder it sttoped working
"""