import os
#code
from flask import Flask, request, render_template, Blueprint, send_file, session, redirect, url_for
from flask import flash
from pymongo import MongoClient
import bcrypt
from .auth import hash_password, verify_password
import os

client = MongoClient(os.environ.get('MONGO_URI'), ssl = True)
db = client['sadsDB']
user_collection = db['AIDB']
app = Flask(__name__, template_folder="templates")
login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        session['email'] = email
        session['password'] = password
        if validate_user():
            return redirect(url_for('home.home_page'))
        else:
            return redirect(url_for('login.signup'))


    return redirect(url_for('home.home_page'))

@login_bp.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')


@login_bp.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('signup.html')

        # Check if user already exists
        existing_user = user_collection.find_one({'email': email})
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('signup.html')

        try:
            hashed_password = hash_password(password)
            user_doc = {
                'email': email,
                'password': hashed_password
            }
            user_collection.insert_one(user_doc)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('home.home_page'))
        except Exception as e:
            flash('An error occurred during registration', 'error')
            return render_template('signup.html')

        # GET request
    return render_template('signup.html')


def validate_user():
    try:
        entered_email = session.get('email')
        entered_password = session.get('password')

        if not entered_email or not entered_password:
            return False

        db_account = user_collection.find_one({"email": entered_email})
        if not db_account:
            return False

        db_password = db_account.get('password')
        return verify_password(db_password, entered_password)
    except AttributeError:
        return False



