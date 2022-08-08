from tokenize import String
from typing import Set
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

# initial Flask application to run on sever
app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='localhost')

# App Secret_key for security purpose
app.secret_key='ac6493790b8221c3c6c965f83646f6322aff93542d880c04f'

# Database connection configuration detail
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ClaimNow'

# Intialize MySQL 
mysql = MySQL(app)

# define favicon location
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

    # defining msg
    msg=''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        # Retrieve variables from Web form 
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE Login_ID = %s AND Login_Password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in user table
        if account:
            # Create session data, session data could pass to other routes
            session['loggedin'] = True
            session['id'] = account['Login_ID']
            session['userid'] = account['UserID']
            session['username'] = account['Employee_Name']
            session['designation'] = account['Department']
            session['role'] = account['Authority']
            session['manager'] = account['Manager']
         
            # Redirect to home page. If admin, will redirect to manageemployee.html. Other roles will redirect to home.html
            if session['role'] == "admin":
                    return redirect(url_for('manageemployee',role=session['role']))
            return redirect(url_for('home',role=session['role']))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    
    # render HTML UI elements based on index.html 
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
        cursor.execute('SELECT * FROM expense_claim LEFT JOIN status ON status.StatusID=expense_claim.StatusID WHERE UserID="%s"',(session['userid'],))
        claims = cursor.fetchall()
        
        #calculate reamining 
        total_claim = 0
        eligibility = 0 
        for row in claims:
            total_claim += row['Claim_Amount_SGD']
            eligibility=row['Current_Eligible']
        remaining=(eligibility-total_claim)
        remaining=round(remaining,2)

        # retrieve users monthly eligibility and pass to home page for statistics 
        cursor.execute('SELECT Monthly_Eligible FROM user WHERE UserID="%s"',(session['userid'],))
        Monthly_Eligible = cursor.fetchone()
        Eligible=Monthly_Eligible['Monthly_Eligible']

        # render HTML UI elements based on home.html 
        return render_template('home.html', remaining=remaining,claims=claims,Eligible=Eligible,username=session['username'], designation=session['designation'],userid=session['userid'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing approve claims page
# Only accessible for loggedin users with Manager role
# http://34.87.75.110:5000/claimnow/approveclaims 
@app.route('/claimnow/approveclaims')
def approveclaims():
   
    # Check if user is loggedin
    if 'loggedin' in session:
        
        # Fetch all data in expense_claim table by logged in manager
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user.Employee_name, expense_claim.*, status.Status_Desc FROM expense_claim LEFT JOIN status ON expense_claim.StatusID = status.StatusID LEFT JOIN user ON expense_claim.UserID = user.UserID WHERE expense_claim.Manager=%s',(session['username'],))
        claims = cursor.fetchall()

        # render HTML UI elements based on approveclaims.html
        return render_template('approveclaims.html',claims=claims,username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing SubmitClaim page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/submitclaim
@app.route('/claimnow/submitclaim', methods=['GET', 'POST'])
def submitclaim():

    # Define mysql cursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:
        
        # check if html form passing as POST method
        if request.method == 'POST':
            ## statusid
                # 1 = New
                # 2 = Submitted
                # 3 = Deleted
                # 4 = Approved
                # 5 = Rejected
                # 6 = Paid
            
            # retrive variables from claim form. And defining other variables (status default as new claim, Manager s current logged in user's manager)
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
            Manager = session['manager']

            # Insert new claim into database
            cursor.execute('INSERT INTO expense_claim (UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',(UserID, Claim_Category, Country_of_Exp, Claim_Amount_SGD, Foreign_Currency, Claim_Amount_FC, Forex, Claim_Desc, Claim_Date, StatusID, Manager))
            mysql.connection.commit()

            # Redirect to history page.
            return redirect(url_for('history',username= session['username'], designation=session['designation'],role=session['role']))
        
        # render HTML UI elements based on submitclaim.html
        return render_template('submitclaim.html',username= session['username'], designation=session['designation'],role=session['role'])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing History page 
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/history
@app.route('/claimnow/history')
def history():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Fetch all data in claims table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM expense_claim LEFT JOIN status ON expense_claim.StatusID=status.StatusID  WHERE expense_claim.UserID=%s',(session['userid'],))
        claims = cursor.fetchall()

        # render HTML UI elements based on history.html
        return render_template('history.html',claims=claims,username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to edit claims
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/editclaim
@app.route('/claimnow/editclaim', methods=['GET', 'POST'])
def editclaim():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Retrieve variables from web form
        claimid=request.form['ClaimID']
        claimid=int(claimid)

        # Retrive the information from selected claim
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM expense_claim LEFT JOIN status ON expense_claim.StatusID=status.StatusID WHERE expense_claim.ClaimID=%s',(request.form['ClaimID'],))
        claims= cursor.fetchone()

        # render HTML UI elements based on editclaim.html
        return render_template('editclaim.html',claims=claims,username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing Add employee page
# Only accessible for loggedin users with Manager role
# http://34.87.75.110:5000/claimnow/createuser
@app.route('/claimnow/createuser', methods=['GET', 'POST'])
def createuser():
    # define mysql cursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # check if html form passing as POST method
        if request.method == 'POST':
            
            # Retrieve varaibles from User Creation Form
            Employee_Name=request.form['Employee_Name']
            Login_ID=request.form['Login_ID']
            Login_Password=request.form['password']
            Department=request.form['Department']
            Level=request.form['Level']
            Monthly_Eligible=request.form['Monthly_Eligible']
            Authority=request.form['Authority']
            Date_Created=datetime.now()
            
            # Identified Direct Manager
            if Level=="3":
                if Department == "Human Resources":
                    Manager="Estebelle Khong"
                elif Department=="IT":
                    Manager="Tay Chia Shin"
                elif Department=="Finance":
                    Manager="Lim Rong Yi"
                elif Department=="Marketing":
                    Manager="Wan Wee Kai"
                elif Department=="Sales":
                    Manager="Mohamad Hamsin Nashrudin"
                else: 
                    Manager="Wong KK"
            else:
                Manager="Wong KK"

            # Insert new record into user table      
            cursor.execute("INSERT INTO user (Employee_Name, Login_ID, Login_Password, Department, Level, Monthly_Eligible, Authority, Manager) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(Employee_Name,Login_ID,Login_Password,Department, Level, Monthly_Eligible,Authority,Manager,))
            mysql.connection.commit()

            # Redirect to employee list page. 
            return redirect(url_for('manageemployee',Manager=Manager,Department=Department,username= session['username'], designation=session['designation'],role=session['role']))
       
        # render HTML UI elements based on createuser.html
        return render_template('createuser.html',username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing Manage employee page
# Only accessible for loggedin users with Manager role
# http://34.87.75.110:5000/claimnow/manageemployee
@app.route('/claimnow/manageemployee')
def manageemployee():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Fetch all data in claims table. 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE NOT UserID=1 AND NOT UserID=2')
        users = cursor.fetchall()

        # render HTML UI elements based on manageemployee.html
        return render_template('manageemployee.html',users=users,username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Accessing Edit User page
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/edituserpage
@app.route('/claimnow/edituserpage', methods=['GET', 'POST'])
def edituserpage():
    # Check if user is loggedin
    if 'loggedin' in session:

        # Retrive the information from selected user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        userid=request.form['UserID']
        cursor.execute('SELECT * FROM user WHERE UserID=%s',(request.form['UserID'],))
        user= cursor.fetchone()

        # render HTML UI elements based on manageemployee.html
        return render_template('edituser.html',user=user,username=session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# Accessing notifications page 
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/notifications
@app.route('/claimnow/notifications')
def notifications():
    
    # Check if user is loggedin
    if 'loggedin' in session:
        # render HTML UI elements based on notifications.html
        return render_template('notifications.html',username= session['username'], designation=session['designation'],role=session['role'])
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



#################################
##      Non-UI Functions      ###
#################################

# Function to approve claims
# Only accessible for loggedin users with Manager role
# http://34.87.75.110:5000/claimnow/approve 
@app.route('/claimnow/approve', methods=['GET', 'POST'])
def approve():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Update claim status to approve
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE expense_claim SET StatusID = 4 WHERE ClaimID=%s',(request.form['ClaimID'],))
        mysql.connection.commit()
        
        # Redirect to claims' list page. 
        return redirect(url_for('approveclaims',username= session['username'], designation=session['designation'],role=session['role']))
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to reject claims
# Only accessible for loggedin users with Manager role
# http://34.87.75.110:5000/claimnow/reject 
@app.route('/claimnow/reject', methods=['GET', 'POST'])
def reject():
    
    # Check if user is loggedin
    if 'loggedin' in session:
        
        # Update claim status to reject
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE expense_claim SET StatusID = 5 WHERE ClaimID=%s',(request.form['ClaimID'],))
        mysql.connection.commit()

        # Redirect to claims' list page. 
        return redirect(url_for('approveclaims',username= session['username'], designation=session['designation'],role=session['role']))
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to delete claims
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/deleteclaim 
@app.route('/claimnow/deleteclaim', methods=['GET', 'POST'])
def deleteclaim():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Update claim status to delete
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM expense_claim WHERE ClaimID=%s;',(request.form['ClaimID'],))
        mysql.connection.commit()
        
        # Redirect to claims' list page. 
        return redirect(url_for('history',username= session['username'], designation=session['designation'],role=session['role']))
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to edit claims
# Only accessible for loggedin users
# http://34.87.75.110:5000/claimnow/edit 
@app.route('/claimnow/edit', methods=['GET', 'POST'])
def edit():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # define mysql cursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # check if html form passing as POST method
        if request.method == 'POST':

            # Retrieve variables from web form. Also current userid from session and current user's manager from session 
            Country_of_Exp = request.form['Expense_Country']
            Claim_Amount_SGD = request.form['Claim_Amount_SGD']
            Foreign_Currency = request.form['primary']
            Claim_Amount_FC = request.form['Claim_Amount_FC']
            Forex = request.form['conversion_rate']
            Claim_Desc = request.form['Claim_Desc']
            Claim_Date = request.form['Claim_Date']
            UserID = session['userid']
            StatusID = 1
            Manager = session['manager']

            # Update claim info
            cursor.execute('UPDATE expense_claim SET Country_of_Exp=%s, Claim_Amount_SGD=%s, Foreign_Currency=%s, Claim_Amount_FC=%s, Forex=%s, Claim_Desc=%s, Claim_Date=%s, StatusID=%s WHERE ClaimID=%s',(Country_of_Exp,Claim_Amount_SGD,Foreign_Currency,Claim_Amount_FC,Forex,Claim_Desc,Claim_Date,StatusID,request.form['ClaimID'],))
            mysql.connection.commit()

            # If manager, redirect to approveclaims.html; If non-manager, redirect to history.html
            if session['role']=="Manager":
                return redirect(url_for('approveclaims',username= session['username'], designation=session['designation'],role=session['role']))
            else:
                return redirect(url_for('history',username= session['username'], designation=session['designation'],role=session['role']))

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to edit employee
# Only accessible for loggedin users with Admin role
# http://34.87.75.110:5000/claimnow/editemployee 
@app.route('/claimnow/editemployee', methods=['GET', 'POST'])
def editemployee():
    
    # Check if user is loggedin
    if 'loggedin' in session:

        # Definr mysal cursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # check if html form passing as POST method
        if request.method == 'POST':

             # Retrieve variables from web form. 
            Employee_Name=request.form['Employee_Name']
            Login_ID=request.form['Login_ID']
            Login_Password=request.form['password']
            Department=request.form['Department']
            Level=request.form['Level']
            Monthly_Eligible=request.form['Monthly_Eligible']
            Authority=request.form['Authority']
            Date_Created=datetime.now()

            # Identified Direct Manager
            if Level=="3":
                if Department == "Human Resources":
                    Manager="Estebelle Khong"
                elif Department=="IT":
                    Manager="Tay Chia Shin"
                elif Department=="Finance":
                    Manager="Lim Rong Yi"
                elif Department=="Marketing":
                    Manager="Wan Wee Kai"
                elif Department=="Sales":
                    Manager="Mohamad Hamsin Nashrudin"
                else: 
                    Manager="Wong KK"
            else:
                Manager="Wong KK"
            
            # Update user info into user table
            cursor.execute('UPDATE user SET Employee_Name=%s, Login_ID=%s, Login_Password=%s, Department=%s, Level=%s, Monthly_Eligible=%s, Authority=%s WHERE UserID=%s',(Employee_Name,Login_ID,Login_Password,Department,Level,Monthly_Eligible,Authority,request.form['UserID'],))
            mysql.connection.commit()
            
            # redirect to employee list
            return redirect(url_for('manageemployee',username= session['username'], designation=session['designation'],role=session['role']))
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Function to delete employee
# Only accessible for loggedin users with Admin role
# http://34.87.75.110:5000/claimnow/deleteemployee 
@app.route('/claimnow/deleteemployee', methods=['GET', 'POST'])
def deleteemployee():
    
    # Check if user is loggedin
    if 'loggedin' in session:
        
        # Delete selected user   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE UserId=%s;',(request.form['UserID'],))
        mysql.connection.commit()
        
        # redirect to employee list
        return redirect(url_for('manageemployee',username= session['username'], designation=session['designation'],role=session['role']))
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))