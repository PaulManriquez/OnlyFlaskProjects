#Programmer: Paul Manriquez 
#Date: May 2024
from flask import Flask, jsonify, request, url_for,  redirect, session, render_template, g 
import sqlite3
import os
#g is a global variable in flask used to store data on it, allows you to access to it the hole proyect
#In Flask, g is a special global object provided by the Flask framework. 
#It is used to store and share data that is globally accessible during a single request 
#but not across different requests. The g object is useful for storing information 
#that should be available globally within the context of a request, such as the current user, 
#database connections, or other resources that are needed in multiple places within a single request.

app = Flask(__name__)
#=====================Flask Settings=======================
app.config['DEBUG'] = True
#Sesion for each user 
app.config['SECRET_KEY'] = 'SecretKeyPassword'
#==========================================================

#============ Data base connection ========================

def connect_db():#Connection Function 
    sql = sqlite3.connect('DataBase/data.db') # Connec
    sql.row_factory = sqlite3.Row #Get a list of dictionaries
    return sql

def get_db():
    if not hasattr(g, 'sqlite3'): # Assure that sqlite3 is in the global variable
        g.sqlite_db = connect_db()
    return g.sqlite_db    

@app.teardown_appcontext # Always a route is called, close the db, prevents memory leak
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

'''
Teardown Function: 
The @app.teardown_appcontext decorator registers a function to be called when the application context ends. 
This is typically after the response has been sent to the client, and it’s the right place to clean up resources to prevent memory leaks.

Function Definition: 
The close_db function is defined to take an error argument, which is required by Flask's teardown functions 
even if it’s not used. This argument will hold any exception that occurred during the request, or None if no error occurred.

Check for Attribute: 
The function checks if the g object has an attribute named sqlite_db using hasattr(g, 'sqlite_db'). 
This is a safe way to check if the database connection was created during the request.

Close the Database Connection: 
If the g object does have an sqlite_db attribute, it calls the close() method on this database connection, ensuring that the connection is properly closed and resources are released.
'''
#==========================================================


@app.route('/')
def index():
    return '<h1> Hello <h1>'


#===== How to establish when you want or not a default name? ================= 
@app.route('/home',methods=['POST', 'GET'], defaults={'name':'Default Name'})
@app.route('/home/<string:name>',methods=['POST','GET'])
def home(name):
    #Generate a session for each user 
    session['name'] = name 
    #===============================
    return '<h1> Hello {} you are in the home page </h1>'.format(name)

@app.route('/json')
def get_json():
    #Read session / retrieve the current session 
    name = session['name']
    #================
    return jsonify({'key': 'value', 'listkey': [1, 2, 3], 'name': name})

#=============================================================================

#====================== Using of  parameters ================================================= 
#Example: http://127.0.0.1:5000/query?name=Paul&location=Japan
@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {} you are from {} . You are in the query page</h1>'.format(name,location)
#=============================================================================================

#========Sending data from a form endpoint to another and be able to process the data========= 
#================= Request data from a form POST method ======================================
#In essendial (/Form1) is a GET (default) endpoint, why? because it displays the form. 
#And when we say (form method="POST") we are stablishg that the data will be send to an endpoint
#that uses this method, in this case (/process) thus is satablished the endpoint like (@app.route('/process',methods=['POST']) )  
@app.route('/Form1')
def Form1_Function():
    #My form is a quick representation of a html file
    #This will send data using POST method to the end point '/process'
    MyForm = '''<form method="POST" action="/process">
                    <input type="text" name="name" placeholder="Enter the name">
                    <input type="text" name="location" placeholder="Enter the location">
                    <!--Button-->
                    <input type="submit" value="Send">
                </form>
                '''
    return MyForm


@app.route('/process',methods=['POST'])
def process_F():
    name = request.form['name']
    location = request.form['location']
    
    db = get_db()
    db.execute('INSERT INTO users (name, location) VALUES (?, ?)',[name,location])
    db.commit()
    print("*****************New user has been added********************")
    #In flask you need to return a response, in this case you can use any of this two
    return '<h1> i got it </h1>'
    #return redirect(url_for('Form1_Function'))
    #=================================================================================
    
    #print("************** I GOT IT ******************")
    #return '<h1> i have your name: {} and location: {}'.format(name,location)

#/form (sends the data) | /process (receive the data) is a POST method because it comes from  a POST method from the form
#========================================================================================================================

#===================Proccessing JsonFiles with postman================================================================
#This endpoint is receiving a json file, this was tested using postman,(PostmanTest3_jason) image 
#Vid10
@app.route('/processJson', methods=['POST'])
def processJson_F():
    #1) get the json sended to this endpoint
    data = request.get_json()
    #2) get the fields of the json file to store in a variable
    name = data['name']# ['name'] = Field to retrieve the data 
    location = data['location']
    randomList = data['randomlist']
    #3) Send the response
    return jsonify({'result':'Sucess','name':name,'location':location,'randomList':randomList})
#====================================================================================================================


#======================Two cases in the same endpoint======================
#==============================REDIRECTION=================================
# * When you enter to the first page, you are in a GET mode, cause' you are loading a form and not necesary sending data (POST mode)
# * Once you push the button 'send', it goes to the same endpoint cause' the line <form method="POST" action="/Form2">, redircts to himself but
#   but, now with a POST method because you have just sended data and is redirecting to another page. 
@app.route('/Form2',methods=['GET','POST'])
def Form2_Function():
    if request.method == 'GET':
    #=======================================<Form2> : Is being redirect to him self 
        MyForm = '''<form method="POST" action="/Form2">
                        <input type="text" name="name" placeholder="Enter the name">
                        <input type="text" name="location" placeholder="Enter the location">
                        <!--Button-->
                        <input type="submit" value="Send">
                    </form>
                    '''
        return MyForm
    else:#Enter to a POST method
        Myname = request.form['name']
        return redirect(url_for('home', name = Myname))
#===========================================================================================


#============================ GET Data from the Data Base ==================================
@app.route('/DataBaseResults')
def viewresults_F():
    db = get_db()
    cur = db.execute('SELECT id, name, location from users')
    results = cur.fetchall()
    return '<h1> ID:{} Name:{} Location:{} </h1>'.format(results[1]['id'],results[1]['name'],results[1]['location'])


@app.route('/ShowDataBase')
def ShowContentInDataBase():
    db = get_db() # Conecction
    cur = db.execute('SELECT id, name, location from users') # Write the query
    results = cur.fetchall() #Retrieve the row data
    #Since we are only reading from the data base we dont need a commit sentece to do de query
    return render_template('ShowDataBase.html', results=results)

#===========================================================================================



if __name__ == '__main__':
    app.run(debug=True)