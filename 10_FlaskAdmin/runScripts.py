'''
from app import create_app, db

app = create_app() 

with app.app_context():
    db.create_all()
'''
'''
from app import db, create_app 

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

'''

from app import create_app, db

app = create_app() 

with app.app_context():
    db.create_all()


''' OLD APP 
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()

# Create the application factory function
def create_app():
    app = Flask(__name__)
    
    #============================================================== Settings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_db.db'
    app.config['SECRET_KEY'] = 'secret_key'
    #==============================================================
    
    db.init_app(app)  # Initialize the database with the app
    
    #===================================================== User Table
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        username = db.Column(db.String(20))
        password = db.Column(db.String(50))
        age = db.Column(db.Integer)
        birthday = db.Column(db.DateTime)
        #
        comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.username)
    #=====================================================
    
    #===================================================== Comment Table
    class Comment(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        comment_text = db.Column(db.String(200))
        #
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

        def __repr__(self):
            return '<Comment %r>' % (self.user_id)

    #=====================================================
    
    # Create admin interface
    admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')
    
    # Model views
    #class UserView(ModelView):
     #   column_searchable_list = ['username']
    
    class CommentView(ModelView):
        column_display_pk = True 
        column_hide_backrefs = False 
        column_list = ('id','comment_text','user_id')
        form_columns = ('comment_text', 'user_id')  # Show user as a dropdown

        

        
        
    admin.add_view(ModelView(User, db.session))
    admin.add_view(CommentView(Comment, db.session))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


'''



