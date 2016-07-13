# Travel-Planner

CS 4400 - Intro to Database Systems
Project Members
- Siddarth Senthilkumar
- Varun Ballari
- Siddhi Shah
- Vooha Vellanki
- Soham

Note: To use the database functionality, before you run the application for the first time, you will need to do the following.
1. Click "Clone and Download" on the top right corner of the page (green button).
2. Type `mysql -u root -p < team1-schema.sql` into your terminal.
3. Enter your mysql password.
4. Type `use team1` into the mysql shell.
5. Exit the mysql shell.

## To run application:
1. Open up terminal and change directory (cd) until your current working directory is the directory containing "views.py".
2. Type `python views.py` and hit enter.
3. Open up any web browser on the same machine and go to the address `localhost:5000`.

## Functionality
Home Page
  Click on the login/register button from the home page to create an account.
Login Page
  You may register a new account by entering all the form data under the "register" section and clicking submit.
  You may login under the login section by entering your username and password and clicking submit.
  Your password will be hashed and stored as a hash in the database.
  If you want to have some fun, try typing `' OR '1'='1' --` for your username and leave your password blank :)
