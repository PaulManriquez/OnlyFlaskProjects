'''
# init_db.py
from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")

#Last 3Vid
'''

from app import create_app,db,User 

Paul = User(username = 'Paul')
app = create_app()
with app.app_context():
    db.session.add(Paul)
    db.session.commit()
