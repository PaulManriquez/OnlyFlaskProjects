from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql3712030:TcvCv1BD1e@sql3.freemysqlhosting.net/sql3712030'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True 

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)
app.app_context().push()# <--- this is important to enable the manipulation of the app.py in the linux shell. 

# Define a model ================================================== TEST Table
class User(db.Model): #User : name of the table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
#=============================================================================

#Create table
class Member(db.Model): #Table name
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(30))
    email = db.Column(db.String(50))
    join_date = db.Column(db.DateTime)

    def __repr__(self): # When is called, get the string representation of the instance
        return '<Member %r>' % self.username

# Create the database tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)