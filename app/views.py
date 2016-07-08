from flask import render_template
from flask import request
import hashlib
from app import app

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/login.html')
def login():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def verify_credentials():
	name=request.form['login_username']
	password=hashlib.sha256(request.form['login_password'].encode('utf-8')).hexdigest()
	return "Username: " + name + "\nPassword: " + password

@app.route('/register', methods=['POST'])
def register():
	name=request.form['register_username']
	password=hashlib.sha256(request.form['register_password'].encode('utf-8')).hexdigest()
	firstname=request.form['register_firstname']
	lastname=request.form['register_lastname']
	email=request.form['register_email']
	street=request.form['register_streetaddress']
	city=request.form['register_city']
	state=request.form['register_state']
	zipcode=request.form['register_zip']
	return name + " " + password + " " + firstname + " " + lastname + " " + email + " "+ street + " " + city + " " + state + " " + zipcode