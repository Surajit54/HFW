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
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= NOTICE MODEL =================
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    memo_no = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================= RECRUITMENT MODEL =================
class Recruitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    details = db.Column(db.String(300))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ================= FUNCTIONS =================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_memo_number():
    year = datetime.now().year
    last = Notice.query.order_by(Notice.id.desc()).first()

    if last and last.memo_no:
        last_no = int(last.memo_no.split("/")[0])
        new_no = last_no + 1
    else:
        new_no = 1

    return f"{str(new_no).zfill(3)}/{year}"

# =========================================================
#                HOME PAGE
# =========================================================
@app.route("/")
def main_home():
    return render_template("main_home.html")


# =========================================================
#                     NOTICE PORTAL
# =========================================================
@app.route("/notices")
def home():

    notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "home.html",
        notices=notices
    )


# =========================================================
#                     RECRUITMENT PAGE
# =========================================================
@app.route("/recruit")
def recruit():

    recruitments = Recruitment.query.order_by(
        Recruitment.id.desc()
    ).all()

    return render_template(
        "recruit.html",
        recruitments=recruitments
    )


# =========================================================
#                     ADMIN LOGIN
# =========================================================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("dashboard"))

        flash("Invalid Login")

    return render_template("admin_login.html")


# =========================================================
#                    ADMIN DASHBOARD
# =========================================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        title = request.form.get("title")
        date = request.form.get("date")
        category = request.form.get("category")
        file = request.files.get("pdf")

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + filename

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            notice = Notice(
                memo_no=generate_memo_number(),
                title=title,
                date=date,
                category=category,
                filename=filename
            )

            db.session.add(notice)
            db.session.commit()

            flash("Notice Uploaded Successfully")

    notices = Notice.query.order_by(Notice.id.desc()).all()

    return render_template(
        "dashboard.html",
        notices=notices
    )


# =========================================================
#                RECRUITMENT UPLOAD (ADMIN)
# =========================================================
@app.route("/upload_recruit", methods=["GET","POST"])
def upload_recruit():

    if not session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        title = request.form.get("title")
        details = request.form.get("details")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        file = request.files.get("pdf")

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + filename

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            recruit = Recruitment(
                title=title,
                details=details,
                start_date=start_date,
                end_date=end_date,
                filename=filename
            )

            db.session.add(recruit)
            db.session.commit()

            flash("Recruitment Uploaded Successfully")

    return render_template("upload_recruit.html")


# =========================================================
#                     DOWNLOAD NOTICE
# =========================================================
@app.route("/download_notice/<int:id>")
def download_notice(id):

    notice = Notice.query.get_or_404(id)

    notice.downloads += 1
    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        notice.filename,
        as_attachment=True
    )


# =========================================================
#                DOWNLOAD RECRUITMENT PDF
# =========================================================
@app.route("/download_recruit/<int:id>")
def download_recruit(id):

    recruit = Recruitment.query.get_or_404(id)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        recruit.filename,
        as_attachment=True
    )


# =========================================================
#                     DELETE NOTICE
# =========================================================
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


# =========================================================
#                     LOGOUT
# =========================================================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("main_home"))


# =========================================================
#                     RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)

