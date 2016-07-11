----------------------------
-- MULTIVALUED ATTRIBUTES --
----------------------------
-- Don't need to specify NOT NULL for any of the attributes of these
-- Because they're all included as parts of the primary key

DROP TABLE IF EXISTS 'address';
CREATE TABLE IF NOT EXISTS address (

	username VARCHAR(30),

	-- Address
	street_no INTEGER,
	street VARCHAR(50),
	city VARCHAR(50),
	state VARCHAR(20),
	zip VARCHAR(10),

	FOREIGN KEY (username) REFERENCES user(username)
		ON DELETE CASCADE
		-- ON UPDATE CASCADE, -- Usually we can't update usernames
	PRIMARY KEY(username, no, street, city, state, zip)
);

DROP TABLE IF EXISTS 'price';
CREATE TABLE IF EXISTS 'price'(

	price DOUBLE,

	-- Price is a multivalued attribute for PAID_ATTRACTION
	attraction_name VARCHAR(100),
	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name),
		ON DELETE CASCADE,
		ON UPDATE CASCADE,
	PRIMARY KEY(attraction_name, price)
);

DROP TABLE IF EXISTS 'hour';
CREATE TABLE IF NOT EXISTS hour (

	attraction_name VARCHAR(100),
	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name)
		ON DELETE CASCADE,
		ON UPDATE CASCADE,

	start_time TIME,
	end_time TIME,
	day VARCHAR(10),
	PRIMARY KEY(attraction_name, start_time, end_time, day)
);

DROP TABLE IF EXISTS 'timeslot';
CREATE TABLE IF NOT EXISTS timeslot (

	attraction_name VARCHAR(100),
	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name),
		ON DELETE CASCADE,
		ON UPDATE CASCADE,

	start_time TIME,
	end_time TIME,
	num_people INTEGER,
	reservation_ID INTEGER AUTOINCREMENT,

	PRIMARY KEY(attraction_name, start_time, end_time, num_people)
);

----------------------------
-- STRONG ENTITIES --
----------------------------
DROP TABLE IF EXISTS 'user';
CREATE TABLE IF NOT EXISTS user (

	username VARCHAR(30) PRIMARY KEY,
	password VARCHAR(64) NOT NULL,
	email VARCHAR(255) NOT NULL,
	is_admin BOOLEAN NOT NULL,

	-- Name
	firstname VARCHAR(35) NOT NULL,
	lastname VARCHAR(35) NOT NULL,
);

DROP TABLE IF EXISTS 'review';
CREATE TABLE IF NOT EXISTS review (

	review_id INTEGER PRIMARY KEY AUTOINCREMENT,
	title VARCHAR(20) NOT NULL,
	authored_date DATE NOT NULL,
	body TEXT NOT NULL,

	-- 1 user WRITES N reviews
	username VARCHAR(30) NOT NULL, -- This is also the author of the review
	FOREIGN KEY (username) REFERENCES user(username),
		ON DELETE CASCADE,

	-- N reviews IS_ABOUT 1 attraction
	attraction_name VARCHAR(100),
	FOREIGN KEY (attraction_name) REFERENCES attraction(attraction_name),
		ON DELETE CASCADE,
		ON UPDATE CASCADE
);

DROP TABLE IF EXISTS 'creditcard';
CREATE TABLE IF NOT EXISTS creditcard (

	-- Expiration Date
	expmonth INTEGER NOT NULL,
	expyear INTEGER NOT NULL,

	-- Billing Address
	street_no INTEGER NOT NULL,
	street VARCHAR(50) NOT NULL,
	city VARCHAR(50) NOT NULL,
	state VARCHAR(20) NOT NULL,
	zip VARCHAR(10) NOT NULL,

	-- Credentials
	card_number CHAR(16),
	firstname VARCHAR(35),
	lastname VARCHAR(35),

	-- 1 user HAS N creditcard
	username VARCHAR(30) NOT NULL,
	FOREIGN KEY (username) REFERENCES user(username)
		ON DELETE CASCADE,

	PRIMARY KEY(card_number, firstname, lastname)
);

DROP TABLE IF EXISTS 'trip';
CREATE TABLE IF NOT EXISTS trip (

	trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
	booked BOOLEAN NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	total_cost DOUBLE NOT NULL, -- TODO: How do you calculate derived attributes?

	-- 1 creditcard PAYS N trip
	card_number CHAR(16),
	firstname VARCHAR(35),
	lastname VARCHAR(35),
	FOREIGN KEY(card_number, firstname, lastname) REFERENCES creditcard(card_number, firstname, lastname)
		ON DELETE CASCADE,
		ON UPDATE CASCADE
);

DROP TABLE IF EXISTS 'activity';
CREATE TABLE IF NOT EXISTS activity (

	activity_name VARCHAR(100) PRIMARY KEY,
	start_time TIME NOT NULL,
	end_time TIME NOT NULL,
	activity_date DATE NOT NULL,
	attraction_name VARCHAR(100),

	-- 1 trip CONSISTS_OF N activity
	trip_id INTEGER,
	FOREIGN KEY(trip_id) REFERENCES trip(trip_id)
		ON DELETE CASCADE,
		ON UPDATE CASCADE,
	FOREIGN KEY(attraction_name) REFERENCES attraction(attraction_name),
		ON DELETE CASCADE,
		ON UPDATE CASCADE
);

DROP TABLE IF EXISTS 'attraction';
CREATE TABLE IF NOT EXISTS attraction (

	attraction_name VARCHAR(100) PRIMARY KEY,
	description TEXT, -- Not all attractions need a description, so no NOT NULL
	nearest_transport TEXT, -- Assumes this is stored as a string (e.g. Gare du Nord)

	-- Address
	streetno INTEGER,
	street VARCHAR(50),
	city VARCHAR(50),
	state VARCHAR(20),
	zip VARCHAR(10),

);

----------------------------
-- M:N RELATIONSHIPS --
----------------------------

DROP TABLE IF EXISTS 'schedule';
CREATE TABLE IF NOT EXISTS schedule(
	username VARCHAR(30),
	activity_name VARCHAR(100),

	FOREIGN KEY username REFERENCES user(username),
		ON DELETE CASCADE,
	FOREIGN KEY activity_name REFERENCES activity(activity_name),
		ON DELETE CASCADE,
		ON UPDATE CASCADE,
	PRIMARY KEY(username, activity_name)
);
