import mysql.connector
from mysql.connector import Error

def get_db_connection():

    try:
        #Connection to the data base 
        conection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'password',
            db = 'taskaplication'
        )
        #If the connection was successfull | print
        if conection.is_connected():
            print('----------------- -----------------')
            print('Successfull connection to the data base')
            #--------------------------------------
            return conection #return the connection
            #-------------------------------------- 
    
    except Error as e:
        print('************Error in the data base connection************')
        print(f'{e}')

def close_db_connection(conection):
    if conection.is_connected():
        conection.close()
        print('----------------- -----------------')
        print('   The connection has finished     ')
