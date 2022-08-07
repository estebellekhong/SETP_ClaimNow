from mysql_db.db_connect import MySqlConnector
import json
import cgi
import sys

# invoke MySqlConnector
sql_config = 'claim'
mysql_con = MySqlConnector(sql_config)

# Retrive data from Frontend
fs = cgi.FieldStorage()

user_id= fs['username'].value
user_password= fs['password'].value 

query_string = '''select Login_ID from user where LoginID="'''+user_id+'''" AND Login_Password="'''+user_password+'''";'''
data = mysql_con.queryall(query_string)

if data[0][0] == user_id:
    status="match"
