import bcrypt #Module to hash a password
#=== Hash the password functions ===
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt) # <--- Get the password in Bytes format
    return hashed.decode('utf-8') #<--- return the password in string format

def check_password(user_password, hashed_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
#===================================