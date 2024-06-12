from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from wtforms_sqlalchemy.fields import QuerySelectField


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
    
    #==================== View configurations ======================================================
    class CommentView(ModelView):
        column_display_pk = True 
        column_hide_backrefs = False 
        create_modal = True
        column_list = ('id', 'comment_text', 'user.username')
        form_columns = ('comment_text', 'user_id')  # Show user as a dropdown

        form_extra_fields = {
            'user': QuerySelectField('User', query_factory=lambda: User.query, get_label='username')
        }

        
    class Userview(ModelView):
        column_exclude_list = ['password']
        column_display_pk = True
        can_create = True 
        can_edit = True 
        can_delete = True 
        can_export = True 

    #Display 
    #              |ModelView or personalize view
    admin.add_view(Userview(User, db.session))
    admin.add_view(CommentView(Comment, db.session))
    #================================================================================================    
    

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
