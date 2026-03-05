from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# -----------------------------
# DATABASE CREATE
# -----------------------------

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memo TEXT,
        filename TEXT,
        upload_date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# UPLOAD FOLDER
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "notices")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():
    return render_template("home.html")

# -----------------------------
# ADMIN LOGIN
# -----------------------------

@app.route("/admin", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")

        else:
            flash("Invalid Login")

    return render_template("admin_login.html")

# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/admin")

    return render_template("dashboard.html")

# -----------------------------
# NOTICE LIST
# -----------------------------

@app.route("/notices")
def notices():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM notices ORDER BY id DESC")

    notices = c.fetchall()

    conn.close()

    return render_template("notices.html", notices=notices)

# -----------------------------
# UPLOAD NOTICE
# -----------------------------

@app.route("/upload_notice", methods=["GET","POST"])
def upload_notice():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        memo = request.form.get("memo")
        file = request.files.get("notice")

        if file and file.filename != "":

            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)

            upload_date = datetime.now().strftime("%d-%m-%Y")

            conn = sqlite3.connect(DB)
            c = conn.cursor()

            c.execute(
                "INSERT INTO notices (memo, filename, upload_date) VALUES (?,?,?)",
                (memo, filename, upload_date)
            )

            conn.commit()
            conn.close()

            flash("Notice Uploaded Successfully")

            return redirect("/upload_notice")

    return render_template("upload_notice.html")

# -----------------------------
# DELETE NOTICE
# -----------------------------

@app.route("/delete_notice/<int:id>")
def delete_notice(id):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM notices WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/notices")

# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/admin")

# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
