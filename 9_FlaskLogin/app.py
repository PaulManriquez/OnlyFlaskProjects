from flask import Flask, render_template,request, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse, urljoin

login_manager = LoginManager() # Global login instance
db = SQLAlchemy() # Data base instance 

#Safe url
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,target))

#=============================================== Data base SQL Alchemy
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
#=====================================================================    

def create_app():
    app = Flask(__name__) # Flask instantation  of my app 
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' #///: cretate the data base 'here'
    app.config['SQALCHEMY_TRACK_MODIFICATIONS'] = False # Just disable the notifications 

    login_manager.init_app(app)#Set the app as login 
    db.init_app(app) #Instance the db in the app 
    login_manager.login_view = 'login' #If you are not login and a page requires it, you are redirect to the function endpoint called login
                               #|Function endpoint name redirect|

    #Custom messages               <                                                  >
    login_manager.login_message = 'You cannot acces that page, you need to login first'                           

    @login_manager.user_loader # load a user from the database.
    def load_user(user_id):
        return User.query.get(int(user_id)) # get the user object from the user ID stored in the session 
    
    #=================================================== Profile route endpoint
    @app.route('/profile')
    @login_required #An user needs to be login to enter to this route 
    def profile():
        return f'<h1>You are logged in the profile, welcome {current_user.username} </h1>'
    
    #Log in access
    @app.route('/login',methods=['GET','POST'])
    def login():

        #=========================== LOGIN Process
        if request.method == 'POST':
            usernameForm = request.form.get('usernameF')
            user = User.query.filter_by(username=usernameForm).first() #Search for the first coincidence of the user (username='') in the data base
            
            #If the user do not exist, return a message
            if not user:
                return '<h1>The user do not exist </h1>'
            
            #Remember the login | True/False
            rememberU = request.form.get('rememberme')
            #If exist continue 
            login_user(user, remember=rememberU) #Create a session LogIn and | assign if the browser needs to remmember the user 

            if 'next' in session and session['next']:
                if is_safe_url(session['next']):
                    return redirect(session['next'])

            #return f'<h1>You are now logged, welcome {current_user.username}!</h1>'
            return redirect(url_for('Index'))

        session['next'] = request.args.get('next')
        return render_template('login.html')
    #LOGOUT 
    @app.route('/logout')
    @login_required #You can logout if you are login
    def logout():
        userlogout = current_user.username
        logout_user() #<----- Pops ths user
        return f'<h1>The user {userlogout} is now logout!</h1>'
    
    #=================================== Home page 
    @app.route('/')
    def Index():
        return 'You are in the home page'


    return app 