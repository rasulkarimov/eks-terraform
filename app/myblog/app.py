from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
import sqlite3
import os
import json
from datetime import date, timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func

# for testing hpa
import cpu_loadtest

app = Flask(__name__)

# conf database
default_db_uri = 'sqlite:////tmp/test.db'
db_uri = os.getenv('DATABASE_URL', default_db_uri)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    dateOfBirth = db.Column(db.Date, nullable=False)
    
    def __init__(self, username, dateOfBirth):
        self.username = username
        self.dateOfBirth = dateOfBirth

@app.route('/hello/<username>', methods=['PUT'])
def save_user(username):
    if not username.isalpha():
        return jsonify({"error": "Username must contain only letters"}), 400

    data = request.get_json()
    if 'dateOfBirth' not in data:
        return jsonify({"error": "Missing dateOfBirth"}), 400

    try:
        date_of_birth = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format, must be YYYY-MM-DD"}), 400

    if date_of_birth >= date.today():
        return jsonify({"error": "dateOfBirth must be a date before today"}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        user.dateOfBirth = date_of_birth
    else:
        user = User(username=username, dateOfBirth=date_of_birth)
        db.session.add(user)

    db.session.commit()
    return '', 204

@app.route('/hello/<username>', methods=['GET'])
def get_greeting(username):
    if not username.isalpha():
        return jsonify({"error": "Username must contain only letters"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()
    birthday_this_year = user.dateOfBirth.replace(year=today.year)

    if birthday_this_year < today:
        birthday_this_year = user.dateOfBirth.replace(year=today.year + 1)

    days_until_birthday = (birthday_this_year - today).days

    if days_until_birthday == 0:
        message = f"Hello, {username}! Happy birthday!"
    else:
        message = f"Hello, {username}! Your birthday is in {days_until_birthday} day(s)"

    return jsonify({"message": message}), 200

@app.route('/')
def index():
    return 'server is available'

@app.route('/testhpa')
def testhpa():
    cpu_loadtest.main()

if __name__=="__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
