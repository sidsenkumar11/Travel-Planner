DROP DATABASE IF EXISTS team1;
CREATE DATABASE IF NOT EXISTS team1;
USE team1;

DROP TABLE IF EXISTS address;
CREATE TABLE IF NOT EXISTS address (

	address_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	street_no INTEGER,
	street_name VARCHAR(50) NOT NULL,
	city VARCHAR(50) NOT NULL,
	state VARCHAR(20),
	country VARCHAR(50) NOT NULL,
	zip VARCHAR(10) NOT NULL
);


DROP TABLE IF EXISTS user;
CREATE TABLE IF NOT EXISTS user (

	username VARCHAR(30) PRIMARY KEY,
	password VARCHAR(64) NOT NULL,
	email VARCHAR(255) NOT NULL,
	is_admin BOOLEAN NOT NULL,
	first_name VARCHAR(35) NOT NULL,
	last_name VARCHAR(35) NOT NULL,
	address_id INTEGER NOT NULL,
	suspended BOOLEAN NOT NULL,

	FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS creditcard;
CREATE TABLE IF NOT EXISTS creditcard (

	creditcard_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	card_number CHAR(16),
	username VARCHAR(30) NOT NULL,
	first_name VARCHAR(35),
	last_name VARCHAR(35),
	exp_month INTEGER NOT NULL,
	exp_year INTEGER NOT NULL,
	address_id INTEGER NOT NULL,

	FOREIGN KEY (username) REFERENCES user(username)
		ON DELETE CASCADE,

	FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS attraction;
CREATE TABLE IF NOT EXISTS attraction (

	attraction_name VARCHAR(100) PRIMARY KEY,
	description TEXT, # Not all attractions need a description, so no NOT NULL
	nearest_transport TEXT, # Assumes this is stored as a string (e.g. Gare du Nord)
	address_id INTEGER NOT NULL,

	FOREIGN KEY (address_id) REFERENCES address(address_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS trip;
CREATE TABLE IF NOT EXISTS trip (

	trip_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	is_booked BOOLEAN NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	creditcard_id INTEGER NOT NULL,

	FOREIGN KEY(creditcard_id) REFERENCES creditcard(creditcard_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS activity;
CREATE TABLE IF NOT EXISTS activity (

	activity_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	activity_name VARCHAR(100) NOT NULL,
	start_time TIME NOT NULL,
	end_time TIME NOT NULL,
	activity_date DATE NOT NULL,
	attraction_name VARCHAR(100) NOT NULL,
	username VARCHAR(30) NOT NULL,
	trip_id INTEGER NOT NULL,

	FOREIGN KEY(trip_id) REFERENCES trip(trip_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,

	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE
		ON UPDATE CASCADE,

	FOREIGN KEY(username) REFERENCES user(username)
		ON DELETE CASCADE
);


DROP TABLE IF EXISTS price;
CREATE TABLE IF NOT EXISTS price (

	cost DOUBLE PRECISION,
	min_age INTEGER,
	max_age INTEGER,
	group_size INTEGER,
	is_student BOOLEAN,
	attraction_name VARCHAR(100) NOT NULL,

	PRIMARY KEY(attraction_name, cost),

	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS hour;
CREATE TABLE IF NOT EXISTS hour (

	attraction_name VARCHAR(100),
	start_time TIME,
	end_time TIME,
	day VARCHAR(10),

	PRIMARY KEY(attraction_name, start_time, end_time, day),

	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS timeslot;
CREATE TABLE IF NOT EXISTS timeslot (

	timeslot_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	start_time TIME,
	end_time TIME,
	num_people INTEGER,
	attraction_name VARCHAR(100),

	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS review;
CREATE TABLE IF NOT EXISTS review (

	review_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	title VARCHAR(100) NOT NULL,
	authored_date DATE NOT NULL,
	body TEXT NOT NULL,
	username VARCHAR(30) NOT NULL, # This is also the author of the review
	attraction_name VARCHAR(100) NOT NULL,

	FOREIGN KEY (username) REFERENCES user(username)
		ON DELETE CASCADE,

	FOREIGN KEY (attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);


DROP TABLE IF EXISTS reserves;
CREATE TABLE IF NOT EXISTS reserves (

	reservation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	num_people INTEGER NOT NULL,
	start_time TIME NOT NULL,
	end_time TIME
);
