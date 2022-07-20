import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(host='34.87.75.110',
                                         database='ClaimNow',
                                         user='claimnow_admin',
                                         password='P@$$word',
                                         port=3306)
   
    db_Info = connection.get_server_info()
    print("Connected to MySQL Server version ", db_Info)
    cursor = connection.cursor()
    cursor.execute("select * from user")
    record = cursor.fetchall()

    for row in record:
        print(row)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    connection.close()
    print("MySQL connection is closed")