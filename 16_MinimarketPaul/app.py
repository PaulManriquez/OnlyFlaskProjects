from flask import Flask, render_template, request, redirect,url_for,session,flash
from DataBaseConnection import get_db_connection,close_db_connection #Data base personilized module
from HashPassword import hash_password,check_password
from TextFunctions import standardize_length
from datetime import datetime
import io


#=========Flask instances and configurations===========
app = Flask(__name__)
app.secret_key = 'SECRETKEY'
#======================================================
#========== Products in the store =====================
ProductsInCart = {
    'chips': 0,
    'lays':0,
    'cocacola':0,
    'pepsi':0,
    'gamesa':0,
    'marinela':0,
    'television':0,
    'fan':0
}
Prices = {
    'chips': 17,
    'lays':19,
    'cocacola':22.5,
    'pepsi': 12.37,
    'gamesa':11,
    'marinela':9.5,
    'television':2700,
    'fan':300
}
#Stock available to buy
InStock = {
    'chips': 10,
    'lays':20,
    'cocacola': 5,
    'pepsi': 7,
    'gamesa':8,
    'marinela': 1,
    'television':3,
    'fan': 2
}

def DisplayCurrentStock():
    print('<--- Displaying Current Stock --->')
    for item in InStock:
        print(f'{item}:{InStock[item]}')

def DisplayCurrentCart():
    print('<--- Displaying Cart --->')
    for item in ProductsInCart:
        print(f'{item}:{ProductsInCart[item]}')

def CurrentTotal():

    Total = float(0)
    for item, quantity in ProductsInCart.items():
        if quantity >=1:    
            Total += (quantity * Prices[item])
    return round(Total,2) #<-- Return the current total to pay

def ClearTheCart():
    print('<--- Clear Cart --->')
    for item in ProductsInCart:
        ProductsInCart[item] = 0           
#======================================================



@app.route('/')
def MainPage():
    
    return render_template('MainPage.html')

#==== LOGIN USER | ENDPOINT 
@app.route('/login',methods=['GET','POST'])
def LoginPage():
    
    if request.method == 'POST':
        Email = request.form['email']
        Password = request.form['password']
        
        if not Email or not Password:
            return render_template('Login.html', message='Missing password or email') 
        
        try:
            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'
            
            #============== Retrieve Data from the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'SELECT * FROM users WHERE Email = %s'
            cur.execute(sqlQuery, (Email,)) # Write the query with parameterized input
            result = cur.fetchone() # <-- Return a tuple with the data 
            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============   

            #If The email doesnt exist in the data base
            if result is None:  
                return render_template('Login.html',message='The user do not exist, try again')
            
            #Check the password
            PassHashed = result[3].encode('utf-8') #<--- Get in Byte format 
                            #   Form  | Data base  [Password from the Form and From the data base] Verification  
            if check_password(Password,PassHashed):
                #Valid Password | Create a Session 
                session['ID'] = result[0]
                session['NAME'] = result[1]
                session['MAIL'] = result[2]
                session['ISADMIN'] = result[4] #Is admin equals to 1 otherwise is 0 
                session['DELETED'] = result[5] #Status

                #If the user was deleted send it the status 
                if result[5] == 1: 
                    return render_template('Login.html',message='This account was deleted')#Account deleted        
                else:
                    return redirect(url_for('MainPage')) #<-- Login successful, return to main page 
            
            return render_template('Login.html',message='Wrong password')#Wrong password 
            
        except Exception as e:
            return f'Error:{e}'
    
    return render_template('Login.html')


#=== LOGOUT |  ENDPOINT
@app.route('/logout', methods=['GET'] )
def Logout():
    session.clear()
    #<--------- Clear the cart 
    ClearTheCart()
    return redirect(url_for('MainPage'))


#=== Create a New Account
@app.route('/newAccount',methods=['GET','POST'])
def NewAccount():

    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Password = request.form['password']
        
        #Check all the data was filled 
        if not Name or not Email or not Password:
            return render_template('createAccount.html',message='Fill all the data please')

        try:
            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'

            Password = hash_password(Password)
            
            data = (Name,Email,Password,0,0) #<--- New User, Last two = Admin | Deleted

            #============== Insert a new user in the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'INSERT INTO users (Name,Email,Password,Admin,Deleted) VALUES (%s,%s,%s,%s,%s)'
            cur.execute(sqlQuery,data) # Write the query with parameterized input
            db.commit()#<--- Insert the new user in the data base 
            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============   

            return render_template('UserCreated.html')
        except Exception as e:
            return f'Error {e}'
    
    return render_template('createAccount.html')


#=== END POINTS TO RENDER SODAS/FRYINGS/COOKIES/OTHERS

#=== Fries page
@app.route('/fries',methods=['GET'])
def Fries():
    return render_template('Fries.html')

#=== Sodas page
@app.route('/sodas',methods=['GET'])
def Sodas():
    return render_template('Sodas.html')

#=== Cookies page
@app.route('/cookies',methods=['GET'])
def Cookies():
    return render_template('Cookies.html')

#=== Others page
@app.route('/others',methods=['GET'])
def Others():
    return render_template('others.html')

#=====================================================

#=== Add to cart endpoint
@app.route('/addtocart',methods=['POST'])
def AddtoCart():

    try:
        ProductName = request.form['Name']   #Name of the product 
        Page = request.form['Page'] + '.html' #Name of the page where comes the petition
        print(f'-------->{Page}')
        DisplayCurrentCart()
        #Add the item to the cart if there is stock available
        if InStock[ProductName]>=1:
            ProductsInCart[ProductName] +=1 #Add product to your cart
            InStock[ProductName]-=1 #Update the stock available 
            DisplayCurrentCart()
            return render_template(Page,message=True)
        else:
            flash(f'No stock available for product: {ProductName}')
            DisplayCurrentCart()
            return render_template(Page,message=True)
        
    except Exception as e:
        return f'Error: {e}'
    

#=== Render MyCart Page
@app.route('/myCart',methods=['GET','POST'])
def MyCart():
    Total = CurrentTotal()
    return render_template('MyCart.html',ProductsInCart=ProductsInCart,Total=Total,Prices=Prices,InStock=InStock)

#=== Add a new product to the cart endpoint
@app.route('/shoppingCart', methods=['POST'])
def shopping_cart():

    try:
        Product = request.form['item'] #Get the name of the product to perform an operation
        Action = request.form['action'] #Get the action to perform
    
        print(f'-->{Product} {Action}')
    
        #=== Increment or decrement product in the Cart
        if Action == 'increment':
            if InStock[Product] >=1:
                ProductsInCart[Product] +=1 #Add a product to the cart
                InStock[Product]-=1 #Update the total products existing
                return redirect(url_for('MyCart'))
            else: 
                flash(f'No stock available for product: {Product}')
                return redirect(url_for('MyCart'))

        elif Action == 'decrement':
            ProductsInCart[Product] -=1 #Decrement the current cart of the client 
            InStock[Product]+=1 #Return the product to the stock 
            return redirect(url_for('MyCart'))

    except Exception as e:
        return f'Error {e}'


#=== Clear the cart 
@app.route('/clearcart',methods=['POST'])
def ClearCart():
    ClearTheCart()
    return redirect(url_for('MyCart'))

#=== Pay process endpoint
@app.route('/pay',methods=['POST'])
def PayCart():

    try:
        TotalTopay = CurrentTotal()
        #If total to pay equals 0 there is no ticket to process
        if TotalTopay == 0:
            return redirect(url_for('MyCart'))

        customer_id = session['ID'] #Get the ID of the client
        name = session['NAME'] #Get the name of the client

        #=== TXT for the ticket
        #=============== Create the ticket ==============
        CurrentDate = datetime.now()
        CurrentDate = CurrentDate.strftime('%Y-%m-%d %H:%M:%S')
        Text = f'Thanks for buying in Minimarket Paul\n     Date:{CurrentDate} \n'
        Text += 'Product        Price          Quantity\n'
        DivisorLine = '-' * 39
        Text = Text + DivisorLine + '\n'
        #If an item exist in the cart get the string formated to put in  the ticket
        for item, quantity in ProductsInCart.items():
            if quantity >=1:
                productString = standardize_length(f'{item} {Prices[item]} {quantity}',15) #Get product string
                Text = Text + productString
        #final line current ticket

        Text += f'{DivisorLine} \nTotal$:{TotalTopay}'
        print('<--- Ticket --->')
        print(Text)
    except Exception as e:
        return f'Error: {e}'    
    #=================================================

    #======= Create the .txt file ====================
    #<------------ Create the file in byte format -------->
    #File name
    #timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #filename = f'{name}_{timestamp}.txt' #<--- Name of the file 
    #Create the txt and write it 
    #with open(filename, 'w') as file:
        #file.write(Text)
    #    ^
    #    |
    #    | This emulates a normal creation of a file, but with byte format to store it in the data base     
    # Create an in-memory file-like object
    file_content = io.BytesIO()
    file_content.write(Text.encode('utf-8'))  # Write text content as bytes
    file_content.seek(0)  # Reset the file pointer to the beginning    
    #^-----------------^ Crutial understanding what is happening with c language 
    #===================================================================================================

    try:
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
            
        data = (customer_id,name,TotalTopay,file_content.read()) #Touple data to insert in the data base 

        #============== Insert a new user in the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'INSERT INTO sales (customer_id,name,total,receipt) VALUES (%s,%s,%s,%s)'
        cur.execute(sqlQuery,data) # Write the query with parameterized input
        db.commit()#<--- Insert the new user in the data base 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============   
        ClearTheCart()
        print('<------ Current Stock ------>')
        DisplayCurrentStock()
        return redirect(url_for('Thanks'))
    except Exception as e:
        return f'Error {e}'    

 #=== Thanks for your purchase
@app.route('/thanks')
def Thanks():
    return render_template('thanks.html')


#=== MySells and CurrentStock for the Admin

@app.route('/mysells',methods=['GET'])
def MySells():
    try:
        print('<-------------- Current Stock -------------->')
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT * FROM sales'
        cur.execute(sqlQuery) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================

        receipts = []
        for tuple in result:
            if isinstance(tuple[4],bytes):     
                text = tuple[4]
                text=text.decode('utf-8')
                #text = str(text)
                receipts.append(text)

        for item in receipts:
            print(item)          

        return render_template('sells.html',result=result,receipts=receipts)
    except Exception as e:
        return f'Error:{e}'
    

#=== Display the current stock available 
@app.route('/mycurrentstock',methods=['GET'])
def MyCurrentStock():
    try:
        return render_template('MyCurrentStock.html',InStock=InStock)
    except Exception as e:
        return f'error: {e}'

#=== Managin users
@app.route('/usersmanage',methods=['GET','POST'])
def UsersManage():
    if request.method == 'POST':
        try:
            Email = request.form['Email']
            
            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'
            
            #============== Retrieve Data from the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'SELECT Deleted FROM users WHERE Email = %s'
            cur.execute(sqlQuery,(Email,)) # Write the query with parameterized input
            Status = cur.fetchone()
            Status = Status[0]
            
            #=== Toggle  Statate
            Status = Status ^ 1
            #===================
            
            #=== Modify the status in the data base 
            sqlQuery = 'UPDATE users SET Deleted = %s WHERE Email = %s'
            cur.execute(sqlQuery,(Status,Email)) # Write the query with parameterized input
            db.commit()

            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============================================================
            return redirect(url_for('UsersManage'))
        except Exception as e:
            return f'Error: {e}'
    else:
        try:
            print('<-------------- USERS PAGE | (ADMIN) -------------->')
            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'
            
            #============== Retrieve Data from the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'SELECT id,Name,Email,Deleted FROM users WHERE Admin = 0'
            cur.execute(sqlQuery) # Write the query with parameterized input
            result = cur.fetchall() # <-- Return a tuple list with the data 
            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============================================================

            return render_template('UsersPage.html',Users = result)
        except Exception as e:
            return f'Error:{e}'      


#=== Purchases for the user only
@app.route('/mypurchases',methods=['GET'])
def MyPurchases():
    print('<------------ My Purchases Page ------------>')
    try:
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT receipt FROM sales WHERE customer_id = %s'
        cur.execute(sqlQuery,(session['ID'],)) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================

        receipts = []
        for tuple in result:
            if isinstance(tuple[0],bytes):     
                text = tuple[0]
                text=text.decode('utf-8')
                #text = str(text)
                receipts.append(text)

        for item in receipts:
            print(item)          

        #return render_template('sells.html',result=result,receipts=receipts)
        return render_template('MyPurchases.html',receipts=receipts)
    except Exception as e:
        return f'Error:{e}'

    


if __name__ == '__main__':
    app.run(debug=True)
