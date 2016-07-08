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

DROP TABLE IF EXISTS 'hours';
CREATE TABLE IF NOT EXISTS hours (

	attraction_name VARCHAR(100),


);

DROP TABLE IF EXISTS 'time';
CREATE TABLE IF NOT EXISTS time (

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

	-- IS_ABOUT relationship with attraction table
	attraction_name VARCHAR(100),

	FOREIGN KEY (attraction_name) REFERENCES attraction(attraction_name),
	FOREIGN KEY (username) REFERENCES user(username)
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

	-- HAS relationship with user table
	username VARCHAR(30) NOT NULL,

	FOREIGN KEY (username) REFERENCES user(username)
		ON DELETE CASCADE,

	PRIMARY KEY(card_number, firstname, lastname)
);

DROP TABLE IF EXISTS 'activity';
CREATE TABLE IF NOT EXISTS activity (

	name VARCHAR(100) PRIMARY KEY,
	start_time TIME NOT NULL,
	end_time TIME NOT NULL,
	activity_date DATE NOT NULL,
);

DROP TABLE IF EXISTS 'trip';
CREATE TABLE IF NOT EXISTS trip (

	trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
	booked BOOLEAN NOT NULL,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL
);

DROP TABLE IF EXISTS 'attraction';
CREATE TABLE IF NOT EXISTS attraction (

	-- Billing Address
	address_no INTEGER,
	address_street VARCHAR(50),
	address_city VARCHAR(50),
	address_state VARCHAR(20),
	address_zip VARCHAR(10),

);