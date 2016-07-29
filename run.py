from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf import Form
from wtforms import StringField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
import hashlib
import locale
import pymysql
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '8ffe05624dfe0efdf7c7f67288d4f4ce5005e0dfb6a1bc48366ef9906dd0586e'
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8') # To get money formatting

#####################################################################
#                          SQL Queries                              #
#####################################################################
def view_completed_attractions_query():
	 return "select activity_date, attraction.attraction_name, description from activity natural join attraction where activity.username = '" + session['username'] + "' and ((activity_date = CURDATE() and activity_end_time <= CURTIME()) or activity_date < CURDATE());"

def get_trip_cost():
	return "select sum(cost) from activity join trip using (trip_id) where trip_id = " + str(session['current_trip_id']) + ";"

def get_all_activities_in_a_trip():
	return "select activity_date, activity_name, cost, activity_start_time, activity_end_time, activity_id from activity natural join trip where username = '" + session['username'] + "' and is_booked = false;";

def get_current_trip_id():
	return "select trip_id from trip natural join user where trip.is_booked=false and user.username='" + session['username'] + "';"

def add_attraction_to_trip(attraction_name, activity_name, start_time, end_time, date, cost):
	return "insert into activity (activity_name, activity_start_time, activity_end_time, activity_date, attraction_name, username, trip_id, cost) values ('" + activity_name + "', '" + start_time + "', '" + end_time + "', '" + date + "', '" + attraction_name + "', '" + session['username'] + "', " + str(session['current_trip_id']) + ", " + str(cost) + ");"

#####################################################################
#                          WTF FORMS                                #
#####################################################################
class ReviewForm(Form):
    title = StringField('review_title', validators=[DataRequired()])
    body = StringField('review_body', widget=TextArea(), validators=[DataRequired()])

#####################################################################
#                         INDEX/HOME                                #
#####################################################################

# Visit site for first time. Pictures.
@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

# Home page. Displays admin interface if user is admin.
@app.route('/home')
def home():

	# Disallow unlogged in users from requesting homepage.
	if 'username' not in session or session['username'] is '':
		return redirect(url_for('index'))

	return create_trip(no_error=True)

#####################################################################
#                          ADMIN PANEL                              #
#####################################################################

# Delete user from admin panel
@app.route('/delete-user/<username>')
def delete_user(username):

	cursor = db.cursor()
	cursor.execute("delete from user where username='" + username + "';")
	db.commit()

	return redirect(url_for('home'))

# Suspend user from admin panel
@app.route('/suspend-user/<username>')
def suspend_user(username):

	cursor = db.cursor()
	cursor.execute("select suspended from user where username='" + username + "';")
	if cursor.fetchall()[0][0] == 1:
		cursor.execute("update user set suspended=0 where username='" + username + "';")
	else:
		cursor.execute("update user set suspended=1 where username='" + username + "';")
	db.commit()

	return redirect(url_for('home'))

# Make user an Admin from admin panel
@app.route('/make-admin/<username>')
def make_admin(username):

	cursor = db.cursor()
	cursor.execute("update user set is_admin=1 where username='" + username + "';")
	db.commit()

	return redirect(url_for('home'))

#####################################################################
#                        LOGIN / REGISTRATION                       #
#####################################################################

# Login/Registration Page. Redirects to home if already logged in.
@app.route('/login-page')
def login_page():

	# Show login page if not logged in. Redirect to home if already logged in.
	if 'username' not in session or session['username'] == '':
		return render_template('login.html')
	else:
		return redirect(url_for('home'))

# On Login Form Submit. Loads home page or shows error.
@app.route('/login', methods=['POST'])
def verify_credentials():

	# Parse user input fields
	name=request.form['login_username']
	password=hashlib.sha256(request.form['login_password'].encode('utf-8')).hexdigest()

	# Query Database
	cursor = db.cursor()
	cursor.execute("select * from user where username = '" + name + "' and password = '" + password + "';")
	rows = cursor.fetchall()
	error = None

	if rows:
		# User found
		if rows[0][7] != 1:
			# Not suspended
			session['username'] = rows[0][0]
			session['email'] = rows[0][2]
			session['is_admin'] = rows[0][3]
			session['name'] = rows[0][4]

			# Set current trip id for this user.
			query = get_current_trip_id()
			cursor.execute(query)
			trip_ids = cursor.fetchall()

			if len(trip_ids) > 0:
				# There are trips for this user. If no, just make it when they start adding attractions.
				session['current_trip_id'] = trip_ids[0][0]

			return redirect(url_for('home'))
		else:
			# Suspended user
			error='User suspended.'
	else:
		# No such user. Login again.
		error = 'Incorrect username or password. Please try again.'
	return render_template('login.html', error=error)

# Logs out of system and redirects to pictures.
@app.route('/logout')
def logout():

	# Clear out session variables
	session.clear()
	return redirect(url_for('index'))

# On Register Form Submit. Loads home page.
# TODO: Re-fill out correct fields when registration fails.
@app.route('/register', methods=['POST'])
def register():

	# Parse user input fields
	name=request.form['register_username']
	password1=hashlib.sha256(request.form['register_password'].encode('utf-8')).hexdigest()
	password2=hashlib.sha256(request.form['register_password2'].encode('utf-8')).hexdigest()
	firstname=request.form['register_firstname']
	lastname=request.form['register_lastname']
	email=request.form['register_email']
	street=request.form['register_streetaddress']
	city=request.form['register_city']
	state=request.form['register_state']
	country=request.form['register_country']
	zipcode=request.form['register_zip']

	# Check if all user fields filled in
	if name == '' or password1 == '' or password2 == '' or firstname == '' or firstname == '' or lastname == '' or email == '' or street == '' or city == '' or state == '' or country == '' or zipcode == '':
		error = 'Please fill out all the fields.'
		return render_template('login.html', error2=error, scroll="register")

	# Check that passwords match
	if password1 != password2:
		error = 'Passwords do not match.'
		return render_template('login.html', error2=error, scroll="register")

	# Parse street_no from street
	street_no = -1

	# Check that address is valid format
	if len(street.split(" ")) < 3 or not street.split(" ")[0].isdigit():
		error = 'Street Address format not recognized. Please re-enter.'
		return render_template('login.html', error2=error, scroll="register")

	street_no = str(street.split(" ")[0])
	street = street[street.index(" ") + 1:]

	# Write to Database
	cursor = db.cursor()
	cursor.execute("insert into address (street_no, street_name, city, state, country, zip) values ("
			+ street_no + ", '" + street + "', '" + city + "', '" + state + "', '" + country + "', '" + zipcode + "');")

	cursor.execute("insert into user (username, password, email, is_admin, first_name, last_name, address_id, suspended) values ('"
	+ name + "', '" + password1 + "', '" + email + "', false, '" + firstname + "', '" + lastname + "', (select max(address_id) from address), 0);")
	db.commit()

	# Update current user session
	session['username'] = name
	session['name'] = firstname
	session['is_admin'] = 0
	session['email'] = email

	return redirect(url_for('home'))

#####################################################################
#                             REVIEWS                               #
#####################################################################

# View Reviews
@app.route('/view-reviews/<attraction_index>')
def view_review(attraction_index):

	# Get attraction_name from the index.
	cursor = db.cursor()
	cursor.execute("select * from attraction;")
	attractions = [dict(name=row[0]) for row in cursor.fetchall()]
	attraction_name = attractions[int(attraction_index) - 1]['name']

	# Get the attraction details using attraction_name.
	query = "select authored_date, body, username, title from review where attraction_name='" + attraction_name + "';"
	cursor.execute(query)
	reviews = [dict(authored_date=row[0], body=row[1], username=row[2], title=row[3]) for row in cursor.fetchall()]

	return render_template('attraction_reviews.html', session=session, reviews=reviews, attraction_name=attraction_name)

# Select visisted attraction to review.
@app.route('/review')
def reviews():

	# Lists a user's visited attractions with a "Review" button.
	cursor = db.cursor()
	query = view_completed_attractions_query()
	cursor.execute(query)
	attractions = [dict(date=row[0], name=row[1], description=row[2]) for row in cursor.fetchall()]
	return render_template('review.html', items=attractions, session=session)

# Write a review for attraction by its name.
@app.route('/write-review/<attraction_index>')
def write_review(attraction_index):

	# Get attraction_name from the index.
	cursor = db.cursor()
	query = view_completed_attractions_query()
	cursor.execute(query)
	attractions = [dict(date=row[0], name=row[1], description=row[2]) for row in cursor.fetchall()]
	attraction_name = attractions[int(attraction_index) - 1]['name']

	# Check if you should be writing reviews for this attraction (visited in past).
	valid_review = False

	for attraction in attractions:
		if attraction['name'] == attraction_name:
			valid_review = True
			break

	if valid_review:
		form = ReviewForm()
		return render_template('review.html', items=attractions, attraction_name=attraction_name, review=1, form=form, session=session)
	else:
		error='You must complete a visit to the attraction before you can review it!'
		return render_template('review.html', items=attractions, error=error, session=session)

# Submit user created review into database.
@app.route('/create-review', methods=['POST'])
def create_review():

	# Insert the review into the database.
	cursor = db.cursor()
	query = "insert into review (title, authored_date, body, username, attraction_name) values ('" + request.form['title'] + "', '" + time.strftime('%Y-%m-%d') + "', '" + request.form['body'] + "', '" + session['username'] + "', '" + request.form['attraction_name'] + "');"
	cursor.execute(query)
	db.commit()

	# Reload the review page, with list of attractions that have been visited by this user.
	query = view_completed_attractions_query()
	cursor.execute(query)
	attractions = [dict(date=row[0], name=row[1], description=row[2]) for row in cursor.fetchall()]
	attraction_name = request.form['attraction_name']

	message = "Created review for " + attraction_name + "!"
	return render_template('review.html', items=attractions, success=message, session=session)

#####################################################################
#                           ATTRACTIONS                             #
#####################################################################

def get_attractions_data():

	cursor = db.cursor()
	cursor.execute("select * from attraction natural join address;")
	attractions = [dict(name=row[1], description=row[2], nearest_transport=row[3], 
		address=(str(row[4]) if row[4] is not None else "") + " " + (row[5] if row[5] is not None else "") + " " + (row[6] if row[6] is not None else "") + ", " + (row[7] if row[7] is not None else "") + " " + (row[8] if row[8] is not None else "") + " " + (row[9] if row[9] is not None else "")) for row in cursor.fetchall()]

	for i in range(0, len(attractions)):

		attraction = attractions[i]
		attraction_name = attraction['name']

		# Add hours into attractions list
		cursor.execute("select day, hour_start_time, hour_end_time from hour natural join attraction where attraction.attraction_name='" + attraction_name + "';")
		hours = [dict(day=row[0], hour_start_time=row[1], hour_end_time=row[2]) for row in cursor.fetchall()]
		attractions[i]['hours'] = hours

		# Add time slots into attractions list

		# 1) Get remaining spots for a time slot.
		cursor.execute("select timeslot_num_people - sum(reserves_num_people) from timeslot natural join reserves where timeslot.attraction_name = '" + attraction_name + "' group by timeslot_id;")
		num_remaining = cursor.fetchall()

		if len(num_remaining) > 0:

			# 2) Get timeslot information.
			cursor.execute("select timeslot_id, timeslot_start_time, timeslot_end_time, timeslot_num_people from timeslot natural join attraction where attraction.attraction_name='" + attraction_name + "';")
			timeslots = []
			rows = cursor.fetchall()
			for j in range(0, len(num_remaining)):
				row = rows[j]
				timeslot = dict(id=row[0], start_time=row[1], end_time=row[2], num_remaining=num_remaining[j][0])
				timeslots.append(timeslot)

			# 3) Add timeslot information to attractions
			attractions[i]['timeslots'] = timeslots
	return attractions

# Shows all available attractions.
@app.route('/attractions')
def attractions():

	attractions = get_attractions_data()
	return render_template('attractions.html', items=attractions, session=session)

# Receive attraction data to turn into an activity
@app.route('/add-to-trip/<attraction_index>', methods=['GET'])
def add_to_trip(attraction_index):

	# TODO: Check if the attraction_name is on list of attractions

	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	cursor = db.cursor()

	# Check if it was a reserved attraction.
	if 'is_reserved' in request.form and request.form['is_reserved']:

		# Reserved
		timeslot_id = request.form['timeslot_id']
		num_people = request.form['num_people']

		# Update database
		cursor.execute("insert into reserves (reserves_num_people, timeslot_id, username) values (" + str(num_people) + ", " + str(timeslot_id) + ", '" + session['username'] + "');")

	# Get attraction name from index.
	cursor.execute("select * from attraction;")
	attractions = [dict(attraction_name=row[0], description=row[1], nearest_transport=row[2]) for row in cursor.fetchall()]
	attraction_name = attractions[int(attraction_index) - 1]['attraction_name']
	db.commit()

	return render_template('create_activity.html', session=session, attraction_name=attraction_name)

# Insert activity into database
@app.route('/create-activity', methods=['POST', 'GET'])
def create_activity():

	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	# Get activity field data.
	attraction_name = request.form['attraction_name']
	activity_name = request.form['activity_name']
	start_time = request.form['start_time']
	end_time = request.form['end_time']
	date = request.form['date']
	cost = request.form['cost'][1:]

	# Add attraction to trip
	cursor = db.cursor()
	query = add_attraction_to_trip(attraction_name, activity_name, start_time, end_time, date, cost)
	cursor.execute(query)
	db.commit()

	success = attraction_name + " added to My Trip!"
	attractions = get_attractions_data()
	return render_template('attractions.html', items=attractions, session=session, success=success)

# Delete an attraction
@app.route('/delete-attraction/<attraction_index>')
def delete_attraction(attraction_index):

	# Get attraction_name
	cursor = db.cursor()
	cursor.execute("select attraction.attraction_name from attraction natural join address;")
	attraction_name = cursor.fetchall()[int(attraction_index) - 1][0]

	# Delete from database
	cursor.execute("delete from attraction where attraction_name='" + attraction_name + "';")
	db.commit()
	return redirect(url_for('home'))

#####################################################################
#                                TRIP                               #
#####################################################################

# Shows current trip itinerary.
@app.route('/trip')
def trip():

	# Create a trip if none exists
	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	# Get activity info for this trip
	cursor = db.cursor()
	query = get_all_activities_in_a_trip()
	cursor.execute(query)
	activities = [dict(date=row[0], name=row[1], price=locale.currency(row[2], grouping=True), start_time=row[3], end_time=row[4], id=row[5]) for row in cursor.fetchall()] # TODO: Correctly map activity info.

	# Calculate total cost of trip
	query = get_trip_cost()
	cursor.execute(query)
	amount = cursor.fetchall()[0][0]
	total_cost = locale.currency(amount, grouping=True) if amount is not None else locale.currency(0, grouping=True)

	return render_template('trip.html', items=activities, session=session, total_cost=total_cost)

@app.route('/complete')
def complete():

	# Create a trip if none exists
	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	# Pay if total cost > 0, else update trip_id record to "booked"
	cursor = db.cursor()
	query = get_trip_cost()
	cursor.execute(query)
	total_cost = cursor.fetchall()[0][0]

	if total_cost is None:
		total_cost = 0

	if total_cost > 0:

		# Check if a credit card is on file for this user.
		query = "select creditcard_id from creditcard, user where user.username='" + session['username'] + "' and user.username=creditcard.username;"
		cursor.execute(query)
		num_cards = len(cursor.fetchall())

		if num_cards is 0:
			# No credit card on file
			return render_template('payment.html', session=session, total_cost=locale.currency(total_cost, grouping=True))
		else:
			# Already have a credit card; they're fine.
			return redirect(url_for('trip_booked'))
	else:
		return redirect(url_for('trip_booked'))

@app.route('/pay', methods=['POST'])
def pay():

	# Create a trip if none exists
	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	card_number="".join(request.form['card_number'].split('-'))
	first_name=request.form['first_name']
	last_name=request.form['last_name']
	exp_month=request.form['expiration_month']
	exp_year=request.form['expiration_year']

	# Get Address ID
	cursor = db.cursor()
	cursor.execute("select address_id from user where username='" + session['username'] + "';")
	address_id = cursor.fetchall()[0][0]

	# Insert credit card information
	query = "insert into creditcard (card_number, username, first_name, last_name, exp_month, exp_year, address_id) values ('" + card_number + "', '" + session['username'] + "', '" + first_name + "', '" + last_name + "', " + str(exp_month) + ", " + str(exp_year) + ", " + str(address_id) + ");"

	return redirect(url_for('trip_booked'))

# Render home page once a trip has been successfully booked.
# TODO: Return a Trip ID so that a user can view their previous trips
@app.route('/trip-booked')
def trip_booked():

	# Create a trip if none exists
	if 'current_trip_id' not in session or not session['current_trip_id']:
		return create_trip(no_error=False)

	cursor = db.cursor()
	cursor.execute("update trip set is_booked=1 where trip_id=" + str(session['current_trip_id']) + ";")
	db.commit()

	session['current_trip_id'] = False
	trip_booked_message = "Congratulations! You're all set!"

	# Query database when user is admin for admin panel
	if session['is_admin']:

		# Get user table information.
		cursor = db.cursor()
		cursor.execute("select * from user;")
		users = [dict(is_admin="Yes" if row[3] == 1 else "No", username=row[0], password=row[1], first_name=row[4], last_name=row[5], email=row[2], suspended="Yes" if row[7] == 1 else "No") for row in cursor.fetchall()]

		# Get attraction table information.
		cursor.execute("select * from attraction natural join address;")
		attractions = [dict(name=row[1], description=row[2], nearest_transport=row[3], 
			address=(str(row[4]) if row[4] is not None else "") + " " + (row[5] if row[5] is not None else "") + " " + (row[6] if row[6] is not None else "") + ", " + (row[7] if row[7] is not None else "") + " " + (row[8] if row[8] is not None else "") + " " + (row[9] if row[9] is not None else "")) for row in cursor.fetchall()]

		return render_template("home.html", session=session, users=users, attractions=attractions, trip_booked_message=trip_booked_message)

	return render_template('home.html', session=session, trip_booked_message=trip_booked_message)

def create_trip(no_error):

	# Query database when user is admin for admin panel
	if session['is_admin']:

		# Get user table information.
		cursor = db.cursor()
		cursor.execute("select * from user;")
		users = [dict(is_admin="Yes" if row[3] == 1 else "No", username=row[0], password=row[1], first_name=row[4], last_name=row[5], email=row[2], suspended="Yes" if row[7] == 1 else "No") for row in cursor.fetchall()]

		# Get attraction table information.
		attractions = get_attractions_data()

		if no_error:
			return render_template("home.html", session=session, users=users, attractions=attractions, no_trip="Here, you can start making your first trip!")
		else:
			return render_template("home.html", session=session, users=users, attractions=attractions, no_trip_error="You must first create a new trip!")

	# Not an admin
	if no_error:
		if 'current_trip_id' not in session or not session['current_trip_id']:
			return render_template("home.html", session=session, no_trip="Here, you can start making a new trip!")
		return render_template("home.html", session=session)
	else:
		return render_template("home.html", session=session, no_trip_error="You must first create a new trip!")

# Create a new current trip id for the user
@app.route('/new-trip', methods=['POST'])
def new_trip():

	start_date = request.form['start_date']
	end_date = request.form['end_date']

	cursor = db.cursor()
	query = "insert into trip (is_booked, trip_start_date, trip_end_date, creditcard_id, username) values (0, '" + start_date + "', '" + end_date + "', 1, '" + session['username'] + "');"
	cursor.execute(query)
	db.commit()

	# Set current trip id for this user.
	query = get_current_trip_id()
	cursor.execute(query)
	session['current_trip_id'] = cursor.fetchall()[0][0]
	return redirect(url_for('trip'))

# Remove an activity from a trip
@app.route('/remove-from-trip/<activity_id>')
def remove_from_trip(activity_id):

	# Find out which activity it is from index.
	cursor = db.cursor()
	cursor.execute("delete from activity where activity_id=" + activity_id + ";")
	db.commit()

	return redirect(url_for('trip'))

#####################################################################
#                         MAIN APPLICATION                          #
#####################################################################

# Run the application
if __name__ == '__main__':

	# Note: If your database uses a different password, enter it here.
	db_pass = 'root'

	# Make sure your database is started before running run.py
	db_name = 'team1'
	db = pymysql.connect(host='localhost', user='root', passwd=db_pass, db=db_name)
	app.run(debug=True)
	db.close()