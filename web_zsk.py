import dataBase
import load_file
from os import environ
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    companies = dataBase.get_150_tabel('')
    return render_template("index.html", companies=companies)

@app.route("/search")
def search():
    q = request.args.get("q")
    companies = dataBase.get_150_tabel(q)
    return jsonify(companies)

@app.route("/cod_tabel")
def cod_tabel():
    return render_template("cod_tabel.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if name in ('GIS', 'RAN'):
            session["name"] = request.form.get("name")
            return redirect("/")
    return render_template("login.html")

@app.route("/r_load_file",  methods=['GET', 'POST'])
def r_load_file():
    if not session.get("name"):
        return redirect("/login")
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xml'):
            load_file.load(file)
        else: return render_template("err.html")
    return render_template("load_form.html")

@app.route("/out_file")
def out_file():
    if not session.get("name"):
        return redirect("/login")
    return render_template("out_form.html")

@app.route("/mail_list")
def mail_list():
    if not session.get("name"):
        return redirect("/login")
    return render_template("mail_list.html")


if __name__ == '__main__':
    ip = environ.get('IP_FOR_TEST_ZSK').split(':')
    app.run(host=ip[0], port=ip[1])

