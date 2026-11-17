from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, json
from datetime import datetime
from functools import wraps
from ai_engine import predict

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_BEFORE_DEPLOYMENT"
DB = "medipredict.db"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL, history TEXT NOT NULL, results TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id))""")

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email and a password of at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with db() as con:
                con.execute("INSERT INTO users(name,email,password,created_at) VALUES(?,?,?,?)",
                    (name,email,generate_password_hash(password),datetime.now().isoformat(timespec="seconds")))
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        records = con.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id DESC LIMIT 5",
                              (session["user_id"],)).fetchall()
    return render_template("dashboard.html", records=records)

@app.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    symptom_options = ["fever", "cough", "headache", "sore_throat", "fatigue",
                       "body_ache", "nausea", "vomiting", "diarrhea", "runny_nose",
                       "shortness_of_breath", "chest_pain"]
    if request.method == "POST":
        symptoms = [s for s in request.form.getlist("symptoms") if s in symptom_options]
        history = {
            "age_group": request.form.get("age_group", "adult"),
            "diabetes": request.form.get("diabetes") == "yes",
            "hypertension": request.form.get("hypertension") == "yes",
            "asthma": request.form.get("asthma") == "yes",
            "heart_disease": request.form.get("heart_disease") == "yes",
            "smoking": request.form.get("smoking") == "yes",
            "family_history": request.form.get("family_history") == "yes"
        }
        if not symptoms:
            flash("Please select at least one symptom.", "error")
            return render_template("assessment.html", symptom_options=symptom_options)
        results = predict(symptoms, history)
        with db() as con:
            con.execute("""INSERT INTO predictions(user_id,symptoms,history,results,created_at)
                VALUES(?,?,?,?,?)""", (session["user_id"], json.dumps(symptoms),
                json.dumps(history), json.dumps(results),
                datetime.now().isoformat(timespec="seconds")))
        return render_template("result.html", results=results, symptoms=symptoms)
    return render_template("assessment.html", symptom_options=symptom_options)

@app.route("/history")
@login_required
def history():
    with db() as con:
        records = con.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY id DESC",
                              (session["user_id"],)).fetchall()
    return render_template("history.html", records=records, json=json)

@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms", [])
    history = data.get("history", {})
    return jsonify(predict(symptoms, history))

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "MediPredict AI"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
