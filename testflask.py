from flask import Flask, session, request, render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("testflask.html")
