from flask import Flask, render_template, request, redirect,url_for,session,flash
from DataBaseConnection import get_db_connection,close_db_connection #Data base personilized module
from HashPassword import hash_password,check_password
from TextFunctions import standardize_length
from datetime import datetime
import random
import io


#=== Modules to upload an image  ==========
#=== (Upload A new Product Part) ==========
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'static/Images' #Where the images will be stored 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
import os 
#===============================================================


#=========Flask instances and configurations===========
app = Flask(__name__)
app.secret_key = 'SECRETKEY'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#======================================================
#========== Products in the store =====================
def load_data():
    try:
        db = get_db_connection()
    
        if not db:
            raise Exception("Error in database connection")
        
        cur = db.cursor()
        cur.execute('SELECT product_name, stock, price FROM products') 
        data = cur.fetchall()
        
        cur.close()
        close_db_connection(db)
                            #Product|Fill each product in cart starting from 0 
        products_in_cart =  {row[0]: 0 for row in data}
                            #Product|Stock
        in_stock =          {row[0]: row[1] for row in data}
                            #Product|Price 
        prices =            {row[0]: row[2] for row in data}
        
        print(f'<------------ App Starting ------------>')
        print(products_in_cart,in_stock,prices)

        return products_in_cart, prices, in_stock #<--- Return the original dictionaries 
    
    except Exception as e:
        return f'Error:{e}'

#<><><><> Load data into dictionaries <><><><>
ProductsInCart, Prices, InStock = load_data()

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
    
    #=== Random Display
    Flag = False
    KeysStockGreater1 = [ key for key in InStock.keys() if InStock[key] >=1 ] #Get only In stock products
    if len(KeysStockGreater1) >=5:
        Flag = True
        randomKeys = random.sample(KeysStockGreater1,5)
    elif len(KeysStockGreater1) >=1 and len(KeysStockGreater1) < 5:
        Flag = True
        randomKeys = random.sample(KeysStockGreater1,len(KeysStockGreater1))
    else:
        randomKeys = []   
    #======================================================================================================           
    
    return render_template('MainPage.html',randomKeys=randomKeys,Flag=Flag)

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
    #return redirect(url_for('MainPage'))
    return render_template('Log_Out.html')

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
    try:
        print('<---- Fries Page ---->')
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT product_name, category FROM products WHERE category = "Fries" '
        cur.execute(sqlQuery) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================
        print(result)
        #result[0] = Name of the product
        #result[1] = Category of the product 
        return render_template('Fries.html',Products = result)
    except Exception as e:
        return f'Error:{e}'

#=== Sodas page
@app.route('/sodas',methods=['GET'])
def Sodas():
    try:
        print('<---- Sodas Page ---->')
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT product_name, category FROM products WHERE category = "Sodas" '
        cur.execute(sqlQuery) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================
        print(result)
        #result[0] = Name of the product
        #result[1] = Category of the product 
        return render_template('Sodas.html',Products = result)
    except Exception as e:
        return f'Error:{e}'

#=== Cookies page
@app.route('/cookies',methods=['GET'])
def Cookies():
    try:
        print('<---- Cookies Page ---->')
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT product_name, category FROM products WHERE category = "Cookies" '
        cur.execute(sqlQuery) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================
        print(result)
        #result[0] = Name of the product
        #result[1] = Category of the product 
        return render_template('Cookies.html',Products = result)
    except Exception as e:
        return f'Error:{e}'

#=== Others page
@app.route('/others',methods=['GET'])
def Others():
    try:
        print('<----  Page ---->')
        db = get_db_connection()

        if not db: #If there is an error in the data base connection | Return 
            return f'Error in data base'
        
        #============== Retrieve Data from the data base 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'SELECT product_name, category FROM products WHERE category = "Others" '
        cur.execute(sqlQuery) # Write the query with parameterized input
        result = cur.fetchall() # <-- Return a tuple list with the data 
        cur.close()# <-- close cur connection 
        close_db_connection(db)# <-- close data base connection
        #===============================================================
        print(result)
        #result[0] = Name of the product
        #result[1] = Category of the product 
        return render_template('others.html',Products = result)
    except Exception as e:
        return f'Error:{e}'

#=====================================================

#=== Add to cart endpoint
@app.route('/addtocart',methods=['POST'])
def AddtoCart():

    try:
        ProductName = request.form['Name']   #Name of the product 
        Page = request.form['Page'] + '.html' #Name of the page where comes the petition
        print(f'-------->{Page} {ProductName}')
        DisplayCurrentCart()
        #Add the item to the cart if there is stock available
        if InStock[ProductName]>=1:
            ProductsInCart[ProductName] +=1 #Add product to your cart
            InStock[ProductName]-=1 #Update the stock available 
            DisplayCurrentCart()
            if Page == 'MainPage.html':
                flash(f'New product added: {ProductName}')
                return redirect(url_for('MainPage'))
            else:
                return render_template(Page,message=True,ProductName=ProductName)
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
    global ProductsInCart, Prices, InStock
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

        #============== Inser the data of the sale 
        cur = db.cursor() #Point to the data base
        sqlQuery = 'INSERT INTO sales (customer_id,name,total,receipt) VALUES (%s,%s,%s,%s)'
        cur.execute(sqlQuery,data) # Write the query with parameterized input
        db.commit()#<--- Insert the new data sell in the data base
        #============== Update the Stock
        for item in ProductsInCart:
            sqlQuery = 'UPDATE products SET stock = %s WHERE product_name = %s'
            cur.execute(sqlQuery,(InStock[item],item))
            db.commit()#<--- Update the stock in data base 

        ProductsInCart, Prices, InStock = load_data() # <-- Update data in the app 
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
            
        return render_template('MyPurchases.html',receipts=receipts)
    except Exception as e:
        return f'Error:{e}'

    
#================= Add New Product by the admin ===============================    
@app.route('/AddNewP',methods=['GET','POST'])
def AddNewP():

    try:
        if request.method == 'POST':
            if 'file1' not in request.files:
                flash('No file uploaded')
                return redirect(url_for('AddNewP'))
            
            file1 = request.files['file1'] #<-- Get the file object
            filename = request.form.get('filename') #<-- Name that will have the file 

            ProductName =request.form.get('filename')
            Category = request.form['section']
            Price = request.form['Price']
            Stock = request.form['Stock']

            Data = (ProductName,Price,Stock,Category) 
            #print(f'**********{Data}')
            if not filename or not ProductName or not Category or not Price or not Stock:
                flash('Fill all the data')
                return redirect(url_for('AddNewP'))
            
            #=== Get the original extention of the file
            extension = ''
            if '.' in file1.filename:
                extension = '.' + file1.filename.split('.')[-1]  
            #==========================================
            
            #Name and extention to save the file
            filename = filename + extension

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file1.save(path)
            return render_template('ProductCreated.html',Data=Data,filename=filename) #<-- Return to a page where is being displayed as a product
        else:#GET method

            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'
            
            #============== Retrieve Data from the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'SELECT DISTINCT category FROM products' #<--- unique products
            cur.execute(sqlQuery) # Write the query with parameterized input
            result = cur.fetchall() # <-- Return a tuple list with the data 
            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============================================================
            
            #Results (Available products section in the store)
            List_Results = [item[0] for item in result]
            
            return render_template('AddNewP.html',sections=List_Results)
    except Exception as e:
        return f'Error: {e}'

@app.route('/NewProductAdded',methods=['POST'])
def ConfirmNewP():
    #Store the product or Cancel  
    try:
        if request.form['Name'] == 'GO':  
            Product_Name = request.form['productName']
            Price = request.form['price']
            Stock = request.form['stock']
            Category = request.form['category']
        
            Data = (Product_Name,Price,Stock,Category)
            print(Data)
            print('<><><><>')
            db = get_db_connection()

            if not db: #If there is an error in the data base connection | Return 
                return f'Error in data base'

            #============== Insert a new product in the data base 
            cur = db.cursor() #Point to the data base
            sqlQuery = 'INSERT INTO products (product_name,price,stock,category) VALUES (%s,%s,%s,%s)'
            cur.execute(sqlQuery,Data) # Write the query with parameterized input
            db.commit()#<--- Insert the new product in the data base 
            cur.close()# <-- close cur connection 
            close_db_connection(db)# <-- close data base connection
            #===============   
            return render_template('ProductAdded.html',productName=request.form['filename'],Data=Data)
        else:
            # Delete the previously stored image
            filename = request.form['filename']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"File not found: {file_path}")

            return redirect(url_for('AddNewP'))    
    except Exception as e:
        return f'Error:{e}'
#================= Add New Product by the admin ===============================    
    




if __name__ == '__main__':
    app.run(debug=True, port=5000)
