import os
from flask import Flask, jsonify, render_template, request
import sqlite3


# Configure application
app = Flask(__name__)

# Configure to use SQLite database
conn = sqlite3.connect("website.db");
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
def index():
    """Render map"""
    # on machine, enter "export GOOGLE_API_KEY=[API KEY HERE]"
    # retrieve API KEY and set for app
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set")
    return render_template("index.html", key=os.environ.get("GOOGLE_API_KEY"))
