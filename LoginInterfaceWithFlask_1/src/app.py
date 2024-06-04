from flask import Flask, render_template, redirect, request, url_for, flash
from config import config
#SQL
from flask_mysqldb import MySQL
#Login
from flask_login import LoginManager, login_user, logout_user, login_required
# Models:
from models.ModelUser import ModelUser
# Entities:
from models.entities.User import User

app = Flask(__name__)#Initialze the flask instance here 
db = MySQL(app)#Data base connection 

#============= Login =================
login_manager_app = LoginManager(app) #
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db,id)
#=====================================

#Redirects to Login the root route 
@app.route('/')
def Index():
    return redirect(url_for('Login'))

#HOME ENDPOINT | enabled when a user is registered
@app.route('/home')
def Home():
    return render_template('auth/home.html')

#================================== LOGIN ENPOINT =========================================================================
@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        #print(request.form['username'])
        #print(request.form['password'])

        user = User(0,request.form['username'],request.form['password'])#Create a temporal user to check if the user exist in the data base 
        logged_user = ModelUser.login(db,user)#Introduce the data base were will search and the temporal user instance to search if it exist 
        #print("*********")
        #print(logged_user.id,logged_user.username,logged_user.password,logged_user.fullname)
        #Now logged_user is an object 
        if logged_user:#If the user exist 
            if logged_user.password:#And the password is correct 
                login_user(logged_user)#Pass the instance of the logged user to login_user
                #return 'correct loggin'
                return redirect(url_for('Home'))#<------Redirect to home page 
            else:
                flash("The password is not correct")
                #return 'wrong password'
                return render_template('auth/login.html')
        else:
            flash('User not found')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    
#============================= LOGOUT ENDPOINT ========================================
@app.route('/logout')
def Logout():
    logout_user()
    return redirect(url_for('Login'))
#======================================================================================

#++++++++++++++++++++++++ Enabled just for login users 
@app.route('/protected')
@login_required
def Protected():
    return '<h1>If you are seeing this, you are a logged user!</h1>'


if __name__ == '__main__':
               #from the object (development is pointing to a class) , retrieve the cofigurations   
    app.config.from_object(config['development'])
    app.run()