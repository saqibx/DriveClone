from flask import Flask, request, render_template, Blueprint, send_file, session, redirect, url_for
from pymongo import MongoClient
import os
import gridfs
from bson.objectid import ObjectId
from io import BytesIO

client = MongoClient(os.environ.get('MONGO_URI'), ssl = True)
db = client['sadsDB']
app = Flask(__name__, template_folder="templates")
home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def home_page():
    if "email" in session :
        return render_template('home.html')
    else:
        return render_template('login.html')
