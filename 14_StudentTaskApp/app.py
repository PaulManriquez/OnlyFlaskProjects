from flask import Flask, render_template, request, redirect,url_for,session
from datetime import datetime
from dbConnect import get_db_connection,close_db_connection #Data base personilized module
import bcrypt #Module to hash a password

app = Flask(__name__) #Flask instance
app.secret_key = 'SECRETKEY'

#=== Hash the password functions ===
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_password(user_password, hashed_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
#===================================


#============== Display login page 
@app.route('/')
def Index():
    
    flag = False        #<--- verify if a session has been created  
    if 'name' in session:
        flag = True

    return render_template('Index.html',userExist = flag)  


#===================================Login Process================================================
@app.route('/login',methods=['POST'])
def Login():
    #Get the data from the form 
    email = request.form['email']
    password_form = request.form['password'] 
    
    if not email or not password_form:
        return render_template('index.html',message = 'missing password or email')
    
    db = get_db_connection()#Get a connection with the data base 
    
    if db:
        print('IM HERE <---------------------------')
        cur = db.cursor() # get a pointer to your database
        sqlQuery = "SELECT * FROM users WHERE email = %s" # verify if the email exists
        cur.execute(sqlQuery, (email,)) # Write the query with parameterized input
        result = cur.fetchone() # <-- Return a tuple with the data 
        #-------------------------------
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection    
        if result is not None:
            hashed_password = result[4] # Get the STRING hashed password from the tuple
            hashed_password = hashed_password.encode('utf-8') # Convert to class BYTE
            #print(f'-->{type(hashed_password)} | {hashed_password}')
            
            if check_password(password_form,hashed_password):
                session['name'] = result[1]
                session['surnames'] = result[2]
                session['email'] = result[3]
                
                if result[5] == 1: #If is the admin
                    session['admin'] = result[5]                  
                    return redirect(url_for('Tasks')) #<-- go to task if is valid
                else:
                    session['name'] = result[1]
                    session['surnames'] = result[2]
                    session['email'] = result[3]
                    session['id'] = result[0]
                    return redirect(url_for('StudentPage'))#<-- go to student page 
            else:
                return render_template('index.html',message = 'password or email not valids')
        else:
            return render_template('index.html',message = 'Email or Password no valids')
    else:
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection 
        return 'error connecting with the data base'

    

#This page is for the student ---> Shows your current task status 
@app.route('/studentPage',methods=['GET','POST'])
def StudentPage():

    if request.method == 'POST':
        id_task = request.form['task_id']
        Answer_task = request.form['MyAns']
        #print(f'--> {id_task} {Answer_task}')
        try:
            sqlQuery = 'UPDATE tasks SET Answer_Student = %s, Finish = %s WHERE id = %s'
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(sqlQuery,(Answer_task,1,id_task)) #Update your task, finish
            db.commit() # <-- execute the changes to the data base

            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection 
            return redirect(url_for('StudentPage'))
        except Exception as e:
            return f'Error: {e}' 
    
    try:
        db = get_db_connection()
        cur = db.cursor()
        id_student = session['id']
        #print(id_student)
        sqlQuery = "SELECT title, description,date_task,assigned_to,Finish,Answer_Student,ProfessorComment,id FROM tasks WHERE assigned_to = %s"
        cur.execute(sqlQuery,(id_student,)) #Get all the data of the student 
        Student_tasks = cur.fetchall() #<-- get a list of tuples
        #print(f'--->{Student_tasks}')
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection 
        return render_template('student.html',MyTasks = Student_tasks)
    except Exception as e:
        print(f'Error:{e}')
            
        


#This page if for the addmin to assign a new task
@app.route('/task',methods=['GET'])
def Tasks():
    
    #=== Retrieve the users to assign a new task - students only 
    db = get_db_connection()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM users WHERE admin = 0")
    users_task = cur.fetchall() #<-- get a list of tuples of the students available to assign a task 
    #====================================
    #Get the information of the task that the admin has assigned
    sqlQuery='''
            SELECT  users.name,users.surnames, tasks.title,tasks.description,tasks.Answer_Student, tasks.Finish,tasks.id
            FROM tasks
            JOIN users ON tasks.assigned_to = users.id
            '''
    cur.execute(sqlQuery)
    All_Current_Tasks = cur.fetchall() #<-- list of tuples of all the current task
    #===========================================================
    #print('*******')
    #print(All_Current_Tasks)
    cur.close()#<--- Close db connection 
    close_db_connection(db)
    
    return render_template('task.html',users_task=users_task,All_Current_Tasks=All_Current_Tasks)


#Create a new task and add it to the data base 
@app.route('/newTask',methods=['POST'])
def NewTask():
    title = request.form.get('title')
    description = request.form.get('description')
    assigned_to = request.form.get('assigned_to')
    d = datetime.now()
    date_task = d.strftime('%Y-%m-%d')
    if title and description and assigned_to:
        db = get_db_connection()#Get a connection with the data base 
        if db:
            cur = db.cursor()# get a pointer to your data base
            sqlQuery = 'INSERT INTO tasks (title,description,date_task,assigned_to,finish) VALUES (%s,%s,%s,%s,%s)'
            data = (title,description,date_task,assigned_to,0)
            cur.execute(sqlQuery,data) # <-- write the query
            db.commit() # <-- execute the changes to the data base
            
            cur.close()#=== Close data base connections ===
            close_db_connection(db)
        

    return redirect(url_for('Tasks'))

#EDIT A TASK  - BY THE ADMIN 
@app.route('/EditTask',methods=['POST'])
def EditTaskAdmin():
    task_id = request.form.get('task_id')
    commentTask = request.form.get('ComTask')
    status = request.form.get('Status')#str or None
    
    # Convert status to 1 (completed) or 0 (not completed)
    status = 1 if status else 0

    data = (commentTask,status,task_id)

    db = get_db_connection()#Get a connection with the data base 
    if db:
        cur = db.cursor()# get a pointer to your data base
        #print(f'---->{data}')
        sqlQuery = 'UPDATE tasks SET ProfessorComment = %s, Finish = %s WHERE id = %s'
        cur.execute(sqlQuery,data) # <-- write the query
        db.commit() # <-- execute the changes to the data base
            
        cur.close()#=== Close data base connections ===
        close_db_connection(db)
    else:
        cur.close()#=== Close data base connections ===
        close_db_connection(db)
        return 'Error connection database'            

    return redirect(url_for('Tasks'))

#Delete a task by the admin
@app.route('/deleteTask',methods=['POST'])
def DeleteTaskByTheAdmin():
    taskId_delete = request.form.get('task_id')
    print(f'---->{taskId_delete}')

    try:
        db = get_db_connection()#Get a connection with the data base 
        if db:
            cur = db.cursor()# get a pointer to your data base
            #print(f'---->{data}')
            sqlQuery = 'DELETE FROM tasks WHERE id = %s'
            cur.execute(sqlQuery,(taskId_delete,)) # <-- write the query
            db.commit() # <-- execute the changes to the data base
                
            cur.close()#=== Close data base connections ===
            close_db_connection(db)
        else:
            cur.close()#=== Close data base connections ===
            close_db_connection(db)
            return 'Error connection database'
    except Exception as e:
            return f'Error deleting task: {str(e)}'

    return redirect(url_for('Tasks'))
#=============================================================================================


#=================================== ENDPOINT to clear a session 
@app.route('/logout',methods=['GET'])
def Logout():
    session.clear()
    return redirect(url_for('Index'))


#================================================= Create a new acount
@app.route('/createAccount',methods=['GET','POST'])
def CreateAccount():
    print('IM HERE')
    if request.method == 'POST':
        name = request.form.get('Name')
        surname = request.form.get('Surname')
        email = request.form.get('Email')
        password = request.form.get('Password')
        
        if name and surname and email and password:
            HashedPass = hash_password(password) #<-- Get in bytes
            HashedPass = HashedPass.decode('utf-8')#<-- Convert in string to store in db
            db = get_db_connection()#Get a connection with the data base 
            if db:
                cur = db.cursor()# get a pointer to your data base
                sqlQuery = 'INSERT INTO users (name,surnames,email,password,admin) VALUES (%s,%s,%s,%s,%s)'
                data = (name,surname,email,HashedPass,0)
                cur.execute(sqlQuery,data) # <-- write the query
                db.commit() # <-- execute the changes to the data base 
                
                #----- Close data base connection ----
                cur.close()#close cur connection 
                close_db_connection(db)#close data base connection 
                
                if 'name' in session:#<-- if the request was perform by the admin
                    return redirect(url_for('Tasks'))
                else:                
                    return 'Welcome to your new account!'
    
            return 'data base error connection'
        else:#If you don fill all the data
            return render_template('createAccount.html',message='Please fill all the data')


    return render_template('createAccount.html')


if __name__ == '__main__':
    app.run(debug=True)    


'''
@app.route('/')
def Index():
    db = get_db_connection()#Get a connection with the data base 
    if db:
        cur = db.cursor()# get a pointer to your data base 
        cur.execute("SELECT * FROM myusers")#Write the query
        results = cur.fetchall()#<-- Return a list with the data 
        cur.close()#close cur connection 
        close_db_connection(db)#close data base connection 
        
        return 'YES'
    else:
        return 'an error has happend' 
'''

'''
#
   @app.route('/login',methods=['GET','POST'])
def Login():
    #Get the data from the form 
    email = request.form['email']
    password_form = request.form['password'] 
    
    db = get_db_connection()#Get a connection with the data base 
    if db:
        cur = db.cursor() # get a pointer to your database
        sqlQuery = "SELECT password FROM users WHERE email = %s" # verify if the email exists
        cur.execute(sqlQuery, (email,)) # Write the query with parameterized input
        result = cur.fetchone() # <-- Return a tuple with the data 
            
        if result is not None:
            hashed_password = result[0] # Get the STRING hashed password from the tuple
            hashed_password = hashed_password.encode('utf-8') # Convert to class BYTE
            #print(f'-->{type(hashed_password)} | {hashed_password}')

            if check_password(password_form,hashed_password):
                print('Password is correct!')
            else:
                print('Invalid password!')

'''