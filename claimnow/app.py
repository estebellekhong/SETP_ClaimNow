from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='0.0.0.0')

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ClaimNow'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('/static/bg/favicon.ico')


# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/claimnow/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE Login_ID = %s AND Login_Password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['Login_ID']
            session['username'] = account['Employee_Name']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg='')

# http://localhost:5000/python/logout - this will be the logout page


@app.route('/claimnow/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users


@app.route('/claimnow/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD,  Foreign_Currency,  Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate,  Manager  FROM expense_claim WHERE UserID = %s',(session['id'],))
        data = cursor.fetchall()

        return render_template('home.html', data=data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users


@app.route('/claimnow/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Login_ID = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/submitclaim - this will be the profile page, only accessible for loggedin users
@app.route('/claimnow/submitclaim', methods=['GET', 'POST'])
def submitclaim():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('submitclaim.html')

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/history - this will be the profile page, only accessible for loggedin users
@app.route('/claimnow/history')
def history():
    # Check if user is loggedin
    if 'loggedin' in session:

        return render_template('history.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/notifications - this will be the profile page, only accessible for loggedin users
@app.route('/claimnow/notifications')
def notifications():
    # Check if user is loggedin
    if 'loggedin' in session:

        return render_template('notifications.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
      
    
        record = Sock(name, style, color, quantity, price, updated)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        # create a message to send to the template
        message = f"The data for sock {name} has been submitted."

        if request.method == 'POST':
            ## UserID
            ## Claim_Category
            ## Country_of_Exp
            ## Claim_Amount_SGD
            ## Foreign_Currency
            ## Claim_Amount_FC
            ## Forex
            ## Claim_Desc
            ## Claim_Date
            ## StatusID
            ## Date_LastUpdate
            ## Manager 

            ## statusid
                # 1 = New
                # 2 = Submitted
                # 3 = Deleted
                # 4 = Approved
                # 5 = Rejected
                # 6 = Paid

            UserID = session['id']
            Claim_Category = request.form['Claim_Category']
            Country_of_Exp = request.form['primary']
            Claim_Amount_SGD = request.form['Claim_Amount_SGD']
            Foreign_Currency = request.form['Foreign_Currency']
            Claim_Amount_FC = request.form['Claim_Amount_FC']
            Forex = request.form['primary']
            Claim_Desc = request.form['Claim_Desc']
            Claim_Date = request.form['Claim_Date']
            StatusID = 1
            Date_LastUpdate = datetime.now()
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute('SELECT Manager FROM user WHERE Login_ID = %s',(session['UserID'],))
            account = cursor.fetchone() 
            
            if account:
                # Create session data, we can access this data in other routes
                Manager = account['Manager']

            #'INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager

            # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager)
            cursor.commit() 



    return render_template('add_record.html', message=message)

