#Programmer: Paul Manriquez
#Date: May 2024

from flask import Flask, render_template, g, request, session, redirect, url_for
from Mydatabase import get_db
import os 
#=== Save the real password using a hash method
from werkzeug.security import generate_password_hash, check_password_hash
#==============================================

app = Flask(__name__) #Create an instance of flask 

#Session Management: Flask uses the SECRET_KEY to sign session cookies, ensuring that they cannot be tampered with. 
#This helps prevent session data from being modified by the client.
#Flask uses cookies to store session data on the client side. This data is not stored on the server.
#The SECRET_KEY is used to sign these session cookies. 
#Signing means that Flask generates a cryptographic signature based on the session data and the SECRET_KEY.
app.config['SECRET_KEY'] = os.urandom(24)

#===================================================
#If there is an active connection with the data base 
#Close connection avoiding memory leaks 
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()
#===================================================        

#====================== Get the row information if a user has been login ==========================================
def get_current_user():
    user_result = None 
    
    if 'user' in session: # if exist a sesion open
        user = session['user']#Retrive the name of the user to make the query and start the session
        db = get_db()#Make a connection with the data base
        user_cur = db.execute('SELECT id, name, expert, admin FROM users WHERE name = ?',[user])#execute the query
        user_result = user_cur.fetchone() #Get the row according with the data base where is stored the user 
    
    return user_result    
#===================================================================================================================

@app.route('/')
def Index():
    #Accordig if a user has been login in our page, we need to pass this user to the home page because:
    #1) If a user has been login | i dont need to see the (logout) page
    #2) If a user hasn't login | i need to be able to se the (login) page
    #user = None #by default is none, because we dont know yet if the user exist
    #if 'user' in session:#If exist an user
    #    user = session['user'] #pass who is the user stored in the session dictionary 

    #Since every page need to know, who is login to use its ionformation, we place it in every route
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    db = get_db()#Data base connection 

    #=== Query to show all the questions answered in the main page
    questions_cur = db.execute('SELECT questions.id as question_id, questions.question_text, askers.name as asker_name, experts.name as expert_name  FROM questions JOIN users as askers ON askers.id = questions.asked_by_id JOIN users as experts ON experts.id = questions.expert_id WHERE questions.answer_text IS NOT NULL')
    questions_result = questions_cur.fetchall() #This query interacts with (Question) endpoint 
    #=== |


    return render_template('home.html',user=user, questions = questions_result) 

@app.route('/question/<question_id>')
def Question(question_id):
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    db = get_db()#data base connection

    #=== Show the Question/Answer selected
    questions_cur = db.execute('SELECT questions.question_text, questions.answer_text, askers.name as asker_name, experts.name as expert_name  FROM questions JOIN users as askers ON askers.id = questions.asked_by_id JOIN users as experts ON experts.id = questions.expert_id WHERE questions.id = ?',[question_id])
    question = questions_cur.fetchone()
    #=== |

    return render_template('question.html',user=user, question=question) 

#===================== Register ENDPOINT ============================================
@app.route('/register', methods=['GET','POST'])
def Register():
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================

    if request.method == 'POST': #If a data was sended
        db = get_db() #Connection data base 
        
        #=== Verify that the user being registered doesnt exist
        existing_user_cur = db.execute('SELECT id FROM users WHERE name = ?',[ request.form['name'] ])
        existing_user = existing_user_cur.fetchone()
        if existing_user:#if the user exist, redirect to the same page 
            return render_template('register.html', user=user, error='User already exist')
        #=== |

        #=== If is a new user create it 
        hashedPassword = generate_password_hash(request.form['password'], method='pbkdf2:sha256') #Encripts the password
        name = request.form['name']
        db.execute('INSERT INTO users (name, password, expert, admin) VALUES (?,?,?,?)',[name,hashedPassword,'0','0'])
        db.commit()
        
        #Once the user has been created, login automatically and re direct to Home/index page
        session['user'] = request.form['name']
        return redirect (url_for('Index')) # Return to home page 
    
    return render_template('register.html',user=user) 
#====================================================================================

#====================== LOGIN ENDPOINT ==============================================
@app.route('/login', methods=['GET','POST'])
def Login():
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    error = None 
    if request.method == 'POST':
        db = get_db() # Data base connection
        

        name = request.form['name']
        password = request.form['password']

        # Get the user with that password
        user_cur = db.execute('SELECT id,name,password FROM users WHERE name = ?',[name])
        user_result = user_cur.fetchone()

        if user_result:#If the user exist in the data base| validate/enable the login
            # Validate autentication
            if check_password_hash(user_result['password'], password):
                
                session['user'] = user_result['name'] # Create a session according with who is login 

                return redirect (url_for('Index')) # Return to home page 
            else:
                error = 'The password is incorrect'
        else:
            error = 'The user doesnt exist'       

    return render_template('login.html',user=user,error=error) 
#====================================================================================

#============================== LOGOUT ENDPOINT ======================================
@app.route('/logout')
def Logout():
    session.pop('user', None) # Get rid of the current user login, know there is no one registered
    return redirect(url_for('Index'))
#====================================================================================


#============================= ASK a question ENDPOINT ======================================================================================
#Ask is used and enable to normal users 
@app.route('/ask',methods=['GET' ,'POST'])
def Ask():
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    if not user:#Prevent to enter to the page (users) if there is no user in the app and redirect 
        return redirect(url_for('Login'))
    #============================================================================================
    
    db = get_db() # Connect to the data base/ cause you are always showing the  experts in the home page | or make the query if is a POST method
    if request.method == 'POST':
        db.execute('INSERT INTO questions (question_text, asked_by_id, expert_id) VALUES (?, ?, ?)',[ request.form['question'], user['id'] , request.form['expert'] ])#write the query
        db.commit()#Make the query
        #return 'You have made the Question:{}  to the Expert:{}'.format(request.form['question'], request.form['expert'])
        return redirect(url_for('Index'))
    
    expert_cur = db.execute('SELECT id, name FROM users where expert = 1') # Select the users that are experts 
    expert_results =  expert_cur.fetchall() #Get the list/dictionary of the experts available 
    
    return render_template('ask.html',user=user, experts=expert_results)

#Unanswered and Answer are routes enabled to the expert | unanswered displays the questions to be respond and answer enable to write a answer to that question
@app.route('/unanswered')
def Unanswered():
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    
    if not user:#Prevent to enter to the page (unanswered) if there is no user in the app and redirect 
        return redirect(url_for('Login'))
    #============================================================================================
    
    if user['expert'] == 0:#If the user is not the expert, redirects to the index page 
        return redirect(url_for('Index'))

    db = get_db()#Data base connection 

    questions_cur = db.execute('SELECT questions.id, questions.question_text, users.name FROM questions JOIN users ON users.id = questions.asked_by_id WHERE questions.answer_text IS NULL AND questions.expert_id = ?',[user['id']] )
    questions_results = questions_cur.fetchall() #Retrieve all the current questions unanswered by the expert
    
    return render_template('unanswered.html',user=user,questions=questions_results)

@app.route('/answer/<question_id>', methods=['GET','POST']) #Here the expert will respond the asnwer 
def Answer(question_id): #question_id : comes from unanswered.html
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    
    if not user:#Prevent to enter to the page (users) if there is no user in the app and redirect 
        return redirect(url_for('Login'))
    #============================================================================================
    
    if user['expert'] == 0:#If the user is not the expert, redirects to the index page 
        return redirect(url_for('Index'))

    db = get_db()#Data base connection 

    if request.method == 'POST':#answering the question 
        db.execute('UPDATE questions SET answer_text = ? WHERE id = ?', [request.form['answer'], question_id])
        db.commit()
        return redirect(url_for('Unanswered'))
        #return '<h1>Question ID:{} , Answer:{}</h1>'.format(question_id, request.form['answer'])

    question_cur = db.execute('SELECT id, question_text from questions where id = ?', [question_id] )#Select the question to answer, according with the id 
    question = question_cur.fetchone()#Retrieve the question

    return render_template('answer.html',user=user, question=question) 

#============================================================================================================================================

#=============================== USERS END POINT ============================================================================================
@app.route('/users')
def Users():
    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
    
    if not user:#Prevent to enter to the page (users) if there is no user in the app and redirect 
        return redirect(url_for('Login'))
    #============================================================================================

    if user['admin'] == 0:#If the user is not the admin, redirects to the index page 
        return redirect(url_for('Index'))

    #================Display all the current users in the page ==============
    db = get_db() #Connect with the ddata base
    users_cur = db.execute('SELECT id, name, expert, admin FROM users')
    users_results = users_cur.fetchall() #Retrieve the data 
    #========================================================================

                                  #Who is log in | Data of all the users in the page  
    return render_template('users.html',user=user,users=users_results)

@app.route('/promote/<user_id>')
def Promote(user_id):

    #Since every page need to know, who is login to use its ionformation, we place it in every route=========================================
    user = get_current_user() # If get 'None' means any user has been login , otherwise, it retrive the information of the user that is login
    #========================================================================================================================================
  
    if not user:#Prevent to enter to the page (promote) if there is no user in the app and redirect 
        return redirect(url_for('Login'))
    #============================================================================================

    if user['admin'] == 0:#If the user is not the admin, redirects to the index page 
        return redirect(url_for('Index'))

    #Promote the user according with the id
    db = get_db() #Make a connection 
    db.execute('UPDATE users SET expert = 1 WHERE id = ?', [user_id]) # Write the query
    db.commit() # Execute the query    

    return redirect( url_for('Users') )     

#============================================================================================================================================


#========= MAIN ==========
if __name__ == '__main__':
    app.run(debug=True) 


