from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE =================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ================= UPLOAD =================
UPLOAD_FOLDER = os.path.join("static", "notices")
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= MODEL =================
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    memo_no = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(100))
    date = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ================= HELPERS =================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_memo():
    year = datetime.now().year
    last = Notice.query.order_by(Notice.id.desc()).first()

    if last and last.memo_no:
        try:
            number = int(last.memo_no.split("/")[0]) + 1
        except:
            number = 1
    else:
        number = 1

    return f"{str(number).zfill(3)}/{year}"

# ================= ROUTES =================

@app.route("/")
def main_home():
    return render_template("main_home.html")


# Recruitment Notices
@app.route("/recruit")
def recruit():

    notices = Notice.query.filter(
        Notice.category.ilike("%recruit%")
    ).order_by(Notice.id.desc()).all()

    return render_template(
        "notices.html",
        notices=notices,
        page_title="Recruitment Notices"
    )


# General Notices
@app.route("/notices")
def notices():

    notices = Notice.query.filter(
        Notice.category.in_(["General","Other Notice"])
    ).order_by(Notice.id.desc()).all()

    return render_template(
        "notices.html",
        notices=notices,
        page_title="Notices"
    )


# ================= ADMIN LOGIN =================

@app.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "Mamam5424":

            session["admin"] = True
            flash("Login Successful")

            return redirect(url_for("dashboard"))

        flash("Invalid Login")

    return render_template("admin_login.html")


# ================= DASHBOARD =================

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        title = request.form.get("title")
        category = request.form.get("category")
        date = request.form.get("date")
        file = request.files.get("pdf")

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + filename

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            notice = Notice(
                memo_no = generate_memo(),
                title = title,
                category = category,
                date = date,
                filename = filename
            )

            db.session.add(notice)
            db.session.commit()

            flash("Notice Uploaded Successfully")

            return redirect(url_for("dashboard"))

    notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "dashboard.html",
        notices = notices
    )


# ================= DOWNLOAD =================

@app.route("/download/<int:id>")
def download_file(id):

    notice = Notice.query.get_or_404(id)

    notice.downloads += 1
    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        notice.filename,
        as_attachment=True
    )


# ================= DELETE =================

@app.route("/delete/<int:id>")
def delete_notice(id):

    if not session.get("admin"):
        return redirect(url_for("admin"))

    notice = Notice.query.get_or_404(id)

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], notice.filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(notice)
    db.session.commit()

    flash("Notice Deleted")

    return redirect(url_for("dashboard"))


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("main_home"))


# ================= RUN =================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000, debug=True)