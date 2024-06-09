from flask import Flask, render_template 
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, IntegerField, BooleanField
from wtforms.validators import InputRequired, Length, AnyOf,Email

#========================= LOGIN FORM | with Flask ====================================
class LoginForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired('User name requiered!'),
                                       Length(min=3,max=8, message='Inser n number characters: between 3 and 8')]
                                       )
    password = PasswordField('password',
                             validators= [InputRequired('password required!')]
                             )
    age = IntegerField('age', default=22)
    yesno = BooleanField('yesno')
    email = StringField('email',validators=[Email()])
#======================================================================================    

class User:
    def __init__(self,username,age,email) -> None:
        self.username = username
        self.age = age 
        self.email = email 

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'SecretKey'

    #=== FORM ENDPOINT 
    @app.route('/',methods=['GET','POST'])
    def index():
        user = User(username='Paul',age=26,email='paul@mail.com')#Create a user to populate the form 
        
        form = LoginForm(obj=user) #Instance of Login Form

        if form.validate_on_submit():#If POST and if every input is valid
            return f'<h1>User name: {form.username.data} Password: {form.password.data} Age:{form.age.data} Yes/No:{form.yesno.data} Email:{form.email.data}</h1>'

        return render_template('index.html', form=form)


    return app 