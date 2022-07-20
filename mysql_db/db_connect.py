import configparser
import pymysql

class MySqlConnector(object):
   
    # initiate database conection
    def __init__(self, env=None):
        cf = configparser.ConfigParser()
        cf.read('mysql_db/mysql_config.ini')
        if not env:
            db_env = ''
        else:
            db_env = env
        sec = 'db_{0}'.format(db_env)
        self.db_host = cf.get(sec, 'host')
        self.db_port = cf.getint(sec, 'port')
        self.db_user = cf.get(sec, 'user')
        self.db_pwd = cf.get(sec, 'password')
        self.db_name = cf.get(sec,'db_name')
        self._connect = pymysql.connect(
            host=self.db_host, 
            port=int(self.db_port), 
            user=self.db_user, 
            password=self.db_pwd, 
            charset='utf8',
            db=self.db_name, 
            init_command='set names utf8')

    # Function to query all
    def queryall(self, sql, params=None):
        cursor = self._connect.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result
    
    # Fucntion to update database, include insert function. 
    def update(self, sql, params=None):
        cursor = self._connect.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self._connect.commit()
        finally:
            cursor.close()

    # Function to close connection
    def close(self):
        if self._connect:
            self._connect.close()

    # Get Connect tion info 
    def get_mysql_conn(env=None):
        return MySqlConnector(env)
    

