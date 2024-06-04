from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
#Users constructs an object representing a data|row , in the data base, modeling an user in OOP
class User(UserMixin):
    #Constructor 
    def __init__(self,id,username,password, fullname="") ->None: #Modeling of the Data Base | ->None :  __init__ method does not return any value
        self.id = id 
        self.username = username 
        self.password = password
        self.fullname = fullname

    @classmethod #Enable the access to the method without making an instance
    def check_password(self, hashed_password, password):#This method returns a true or false if the password is correct.   
        return check_password_hash(hashed_password,password)
 
#print(generate_password_hash('password',method='pbkdf2:sha256'))