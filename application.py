import os
from flask import Flask, jsonify, render_template, request, session, redirect, flash
import sqlite3
from helpers import apology, login_required
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
conn = sqlite3.connect("homeify.db");
cursor = conn.cursor();

def getConnection():
    return conn

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Render map"""
    # on machine, enter "export GOOGLE_API_KEY=[API KEY HERE]"
    # retrieve API KEY and set for app
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")
    return render_template("index.html", key=os.environ.get("GOOGLE_API_KEY"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # ensure confirmation email was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)
        # passwords must match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        elif not request.form.get("firstname") or not request.form.get("lastname") or not request.form.get("street") or not request.form.get("secondary") or not request.form.get("city") or not request.form.get("state") or not request.form.get("zip"):
            return apology("all fields required")

        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))
        rows = cursor.fetchall()

        # Error message if username already exists
        if len(rows) == 1:
            return apology("username already exists", 400)
        else:
            # save new user in db
            cursor.execute("INSERT INTO users (username, hash, first_name, last_name, street, secondary, city, state, zip, last_line) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("firstname"), request.form.get("lastname"), request.form.get("street"), request.form.get("secondary"), request.form.get("city"), request.form.get("state"), request.form.get("zip"), request.form.get("city") + ", " + request.form.get("state") + " " + request.form.get("zip")))
            # automatically log in new user and redirect to homepage
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))
            rows = cursor.fetchall()

            session["user_id"] = rows[0][0]
            flash('You were successfully logged in')
            return redirect("/")
    else:
        # if get request, show the register page
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),))
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][4], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        flash('You were successfully logged in')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Successfully Logged out")
    # Redirect user to login form
    return redirect("/")
