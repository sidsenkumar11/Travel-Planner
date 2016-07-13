from flask import Flask, flash, render_template, request, redirect, session, url_for
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
	cursor.execute("select * from user where username = '" + name + "' and password = '" + password + "';")
	rows = cursor.fetchall()
	error = None
	if rows:
		session['username'] = rows[0][0]
		session['email'] = rows[0][2]
		session['name'] = rows[0][4]	
		return redirect(url_for('home'))
	else:
		error = 'Incorrect username or password. Please try again.'
	return render_template('login.html', error=error)

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

	street_no = -1
	# Parse street_no from street
	if street.split(" ")[0].isdigit():
		street_no = street.split(" ")[0]
		street = street[street.index(" ") + 1:]

	street_no = str(street_no)
	cursor = db.cursor()
	cursor.execute("insert into address (street_no, street_name, city, state, zip) values ("
			+ street_no + ", '" + street + "', '" + city + "', '" + state + "', '" + zipcode + "');")
	db.commit()

	cursor.execute("insert into user (username, password, email, is_admin, first_name, last_name, address_id) values ('"
	+ name + "', '" + password + "', '" + email + "', false, '" + firstname + "', '" + lastname + "', 1);")
	db.commit()

	session['username'] = name
	session['name'] = firstname
	return redirect(url_for('home'))

@app.route('/home')
def home():
	if session['username'] is '':
		return redirect(url_for('index'))
	return render_template("home.html", username=session['username'], name=session['name'])

@app.route('/logout')
def logout():
	session['username'] = ''
	return redirect(url_for('index'))

if __name__ == '__main__':
	dbname = 'team1'
	db = pymysql.connect(host='localhost',
			     user='root', passwd='root', db=dbname)
	app.run(debug=True)
	db.close()