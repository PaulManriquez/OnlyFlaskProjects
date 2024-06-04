from .entities.User import User #Since entities is a relative inner path, MAKE SURE TO USE THE DOT AT THE BEGINNING 

class ModelUser():
    @classmethod #Make it usable without stablishing an instance of the object 
                 #Data base connection | user objec 

    def login(self,db,user): #create an object user if the password was validated 
        try:
            cur = db.connection.cursor() #Connect to the tada base 
            sql = """SELECT id, username, password, fullname FROM myusers  
                    WHERE username = '{}' """.format(user.username) # Check for the existence of the username in the data base 
            
            cur.execute(sql)#Write the query
            row = cur.fetchone()#Retrieve the result

            if row != None:#create the user and verify if when is being checked the passwords, are matching 
                                          #|verify the hashed password with the plain text (user.username)  
                user = User(row[0],row[1], User.check_password(row[2], user.password), row[3] )
                return user #return the user object created 
            else:
                return None 
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_by_id(self,db,id):#To know who is loggin in the page 
        try:
            cur = db.connection.cursor()
            sql = 'SELECT id, username, fullname FROM myusers WHERE id = {}'.format(id)
            cur.execute(sql)
            row = cur.fetchone()
            if row :
                return User(row[0],row[1],None,row[2])
            else:
                return None 
        except Exception as e:
            raise Exception(e)            