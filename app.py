from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "secret123"   # session security


# =====================================
# HOME PAGE
# =====================================
@app.route("/")
def home():
    return render_template("home.html")


# =====================================
# GOVT ORDER PAGE
# =====================================
@app.route("/govt_order")
def govt_order():
    return render_template("govt_order.html")


# =====================================
# RECRUITMENT NOTICE PAGE
# =====================================
@app.route("/student")
def student():
    return render_template("student.html")


# =====================================
# ADMIN LOGIN
# =====================================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    # already logged in hole dashboard e pathabe
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # demo login (change later)
        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template(
                "admin_login.html",
                error="Invalid Username or Password"
            )

    return render_template("admin_login.html")


# =====================================
# ADMIN DASHBOARD (Protected)
# =====================================
@app.route("/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin"))

    return render_template("dashboard.html")


# =====================================
# LOGOUT
# =====================================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


# =====================================
# RUN SERVER
# =====================================
if __name__ == "__main__":
    app.run()