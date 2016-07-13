from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '8ffe05624dfe0efdf7c7f67288d4f4ce5005e0dfb6a1bc48366ef9906dd0586e'

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
	cursor = db.cursor()
	cursor.execute("select * from user where username = " + name + " and password = " + password)
	rows = cursor.fetchall()
	if rows:
		print(rows)
		return redirect(url_for('home'))
	else:
		flash('Incorrect username or password, please try again.')
		return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
	cursor = db.cursor()
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

if __name__ == '__main__':
	dbname = 'team1'
	db = pymysql.connect(host='localhost',
			     user='root', passwd='root', db=dbname)
	app.run(debug=True)
	db.close()
