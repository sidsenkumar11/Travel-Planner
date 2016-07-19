# Travel-Planner

A web application that allows users to create travel itineraries for their vacations.

## To run application:
1. Open up terminal and change directory (cd) until your current working directory is the directory containing "run.py".
2. Type `python run.py` and hit enter.
3. Open up any web browser on the same machine and go to the address `localhost:5000`.

### Note:
To use the database functionality, before you run the application for the first time, you will need to do the following.

1. Type `mysql -u root -p < team1-schema.sql` into your terminal.
2. Enter your mysql password.
3. Type `use team1` into the mysql shell.
4. Exit the mysql shell.
5. In the file "run.py", at the bottom, replace the default database password with your own MySQL password.

## Functionality
<b>Home Page</b><br />
&nbsp;&nbsp;&nbsp;&nbsp;- Click on the login/register button from the home page to create an account.

<b>Login Page</b><br />
&nbsp;&nbsp;&nbsp;&nbsp;- You may register a new account by entering all the form data under the "register" section and clicking submit.<br />
&nbsp;&nbsp;&nbsp;&nbsp;- You may login under the login section by entering your username and password and clicking submit.<br />
&nbsp;&nbsp;&nbsp;&nbsp;- Your password will be hashed and stored as a hash in the database.<br />
&nbsp;&nbsp;&nbsp;&nbsp;- If you want to have some fun, try typing `' OR '1'='1' --` for your username and leave your password blank :)
