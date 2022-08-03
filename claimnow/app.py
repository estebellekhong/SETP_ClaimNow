from tokenize import String
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='localhost')

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


###################################
##          Login/Logout         ##
###################################

# Landing page Login function
# http://34.87.75.110:5000/claimnow
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
            session['userid'] = account['UserID']
            session['username'] = account['Employee_Name']
            session['designation'] = account['Department']
            session['role'] = account['Authority']
         
            # Redirect to home page
            if session['role'] == "admin":
                    return redirect(url_for('manageemployee',role=session['role']))
            return redirect(url_for('home',role=session['role']))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)

# Logout function
# http://34.87.75.110:5000/claimnow/logout
@app.route('/claimnow/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

##################################
##          UI rederer          ##
##################################

# Home page 
# only accessibe for loggedin user 
# http://34.87.75.110:5000/claimnow/home
@app.route('/claimnow/home')
def home():
    # Check if user is loggedin
   
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all data in claims table
        cursor.execute('SELECT * FROM expense_claim LEFT JOIN status ON status.StatusID=expense_claim.StatusID')
        #cursor.execute(query)
        claims = cursor.fetchall()

        return render_template('home.html', claims=claims,username=session['username'], designation=session['designation'],userid=session['userid'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing approve claims page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/approveclaims 
@app.route('/claimnow/approveclaims')
def approveclaims():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('approveclaims.html',username= session['username'], designation=session['designation'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing SubmitClaim page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/submitclaim
@app.route('/claimnow/submitclaim', methods=['GET', 'POST'])
def submitclaim():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:
        
        if request.method == 'POST':
            ## statusid
                # 1 = New
                # 2 = Submitted
                # 3 = Deleted
                # 4 = Approved
                # 5 = Rejected
                # 6 = Paid
            
            Claim_Category = request.form['Claim_category']
            Country_of_Exp = request.form['Expense_Country']
            Claim_Amount_SGD = request.form['Claim_Amount_SGD']
            Foreign_Currency = request.form['primary']
            Claim_Amount_FC = request.form['Claim_Amount_FC']
            Forex = request.form['conversion_rate']
            Claim_Desc = request.form['Claim_Desc']
            Claim_Date = request.form['Claim_Date']
            UserID = session['userid']
            StatusID = 1
            cursor.execute('SELECT Manager FROM user WHERE Login_ID = %s',(session['userid'],))
            account = cursor.fetchone() 
            
            if account:
                # Get Manager of current login User
                Manager = account['Manager']
            else:
                Manager=" "

            #'INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager
            cursor.execute('INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',(UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Manager))
            mysql.connection.commit()
            return redirect(url_for('history',username= session['username'], designation=session['designation'],role=session['role']))
        return render_template('submitclaim.html',username= session['username'], designation=session['designation'],role=session['role'])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing History page 
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/history - this will be the profile page, only accessible for loggedin users
@app.route('/claimnow/history')
def history():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch all data in claims table
        cursor.execute('SELECT * FROM expense_claim LEFT JOIN status ON expense_claim.StatusID=status.StatusID  WHERE expense_claim.UserID=%s',(session['userid'],))
        claims = cursor.fetchall()

        return render_template('history.html',claims=claims,username= session['username'], designation=session['designation'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing Add employee page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/createuser
@app.route('/claimnow/createuser', methods=['GET', 'POST'])
def createuser():
    # Check if user is loggedin
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'POST':
            # Retrieve data from User Creation Form
            Employee_Name=request.form['Employee_Name']
            Login_ID=request.form['Login_ID']
            Login_Password=request.form['password']
            Department=request.form['Department']
            Level=request.form['Level']
            Monthly_Eligible=request.form['Monthly_Eligible']
            Authority=request.form['Authority']
            Date_Created=datetime.now()
            
            # Identified Direct Manager
            if Level==0:
                Manager="Wong KK"
            elif Level==1:
                    Manager = Employee_Name
            else:
                #Get department manager
                cursor.execute('SELECT Employee_Name FROM user WHERE Authority="Manager" AND Department="%s"',(Department,))
                Manager = cursor.fetchone()
                if Manager is None:
                    Manager = "Wong KK"
                    
            # Insert User Record      
            cursor.execute("INSERT INTO user (Employee_Name, Login_ID, Login_Password, Department, Level, Monthly_Eligible, Authority, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(Employee_Name,Login_ID,Login_Password,Department, Level, Monthly_Eligible,Authority,Manager,))
            #print("INSERT INTO user (UserID, Employee_Name, Login_ID, Login_Password, Department, Level, Monthly_Eligible, Authority, Manager, Date_Created ) VALUES ("+str(id)+","+Employee_Name+","+Login_ID+","+Login_Password+","+Department+","+str(Level)+","+str(Monthly_Eligible)+","+Authority+","+Manager+","+str(Date_Created)+")")
            mysql.connection.commit()

            return redirect(url_for('manageemployee',Manager=Manager,Department=Department,username= session['username'], designation=session['designation'],role=session['role']))
        return render_template('createuser.html',username= session['username'], designation=session['designation'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing Manage employee page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/manageemployee
@app.route('/claimnow/manageemployee')
def manageemployee():
    
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch all data in claims table
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        return render_template('manageemployee.html',users=users,username= session['username'], designation=session['designation'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing History page 
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/notifications - this will be the profile page, only accessible for loggedin users
@app.route('/claimnow/notifications')
def notifications():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('notifications.html',username= session['username'], designation=session['designation'],role=session['role'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


######################################
##          Core Functions          ##
######################################
# add claim record
# Only accessible for loggedin users
#@app.route('/add_record', methods=['GET', 'POST'])
#def add_record():
    #form1 = AddRecord()
    #if form1.validate_on_submit():
      
    
     #   record = Sock(name, style, color, quantity, price, updated)
        # Flask-SQLAlchemy magic adds record to database
     #   db.session.add(record)
     #   db.session.commit()
        # create a message to send to the template
     #   message = f"The data for sock {name} has been submitted."

      #  if request.method == 'POST':
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

       #     UserID = session['id']
       #     Claim_Category = request.form['Claim_Category']
       #     Country_of_Exp = request.form['primary']
       #     Claim_Amount_SGD = request.form['Claim_Amount_SGD']
       #    Foreign_Currency = request.form['Foreign_Currency']
       #     Claim_Amount_FC = request.form['Claim_Amount_FC']
       #     Forex = request.form['primary']
       #     Claim_Desc = request.form['Claim_Desc']
       #     Claim_Date = request.form['Claim_Date']
       #     StatusID = 1
       #     Date_LastUpdate = datetime.now()
            
       #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
       #     cursor.execute('SELECT Manager FROM user WHERE Login_ID = %s',(session['UserID'],))
       #     account = cursor.fetchone() 
            
       #     if account:
                # Create session data, we can access this data in other routes
       #         Manager = account['Manager']

            #'INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager

            # We need all the account info for the user so we can display it on the profile page
       #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
       #     cursor.execute('INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);', UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Date_LastUpdate, Manager)
       #     cursor.commit() 



   # return render_template('add_record.html', message=message)

