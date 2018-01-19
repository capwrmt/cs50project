import os
from flask import Flask, jsonify, render_template, request
import sqlite3


# Configure application
app = Flask(__name__)

# Configure to use SQLite database
