from flask import Flask, render_template, g, request, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

#============ DATABASE CONNECTION ============
def connect_db():
    sql = sqlite3.connect('DataBase/food_log.db')
    sql.row_factory = sqlite3.Row  # Get a list of dictionaries
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#================= ROOT ENDPOINT ================
@app.route('/',methods=['POST','GET'])
def index():
    #Data base connection
    db = get_db()

    if request.method == 'POST': #If we are writing date in this page 
        date = request.form['date'] #Assumming the date is in YYYY-MM-DD
        #Insert in the correct format 
        print(date)
        dt = datetime.strptime(date,'%Y-%m-%d')
        print(dt)
        database_date = datetime.strftime(dt,'%Y%m%d')
        print(database_date)

        #Write in the data base 
        db.execute('INSERT INTO log_date (entry_date) VALUES (?)',[database_date])
        #Execute query
        db.commit()

    cur = db.execute('''SELECT log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat , sum(food.calories) as calories 
                        FROM log_date 
                        LEFT JOIN food_date ON food_date.log_date_id = log_date.id 
                        LEFT JOIN food on food.id = food_date.food_id 
                        GROUP BY log_date.id ORDER BY log_date.entry_date DESC
                        ''')    
    
    results = cur.fetchall()
    
    DateResults = []
    
    for i in results:
        singleDate = {} 

        singleDate['entry_date'] = i['entry_date'] # type: ignore #Save the dates as it is , with out format | 20170520
        singleDate['protein'] = i['protein']
        singleDate['carbohydrates'] = i['carbohydrates']
        singleDate['fat'] = i['fat']
        singleDate['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']),'%Y%m%d')#2017-07-23 00:00:00
        a = datetime.strftime(d, '%B %d, %Y')#July 23, 2017 string class 
        singleDate['pretty_date'] = a #insert in the key, a new element | the value is being replaced each loop time  and the key is created at first run
        #=====
        #List of dictionaries
        DateResults.append(singleDate) #[{'entry_date': 'July 24, 2017'}, {'entry_date': 'July 23, 2017'}]

    return render_template('home.html', results=DateResults)    

#================ VIEW ENDPOINT =================
@app.route('/view/<date>', methods=['GET', 'POST'])
def view_F(date):
    db = get_db()#Connect to the data base 
    
    cur = db.execute('SELECT id, entry_date FROM log_date WHERE entry_date = ?',[date])
    date_result = cur.fetchone() #since we are expecting to retrieve just one element, we use (fetch one), retriving just one row

    if request.method == 'POST':
        #Create a relation between the product that you consumed, and the date where was eaten 
        #in the table called: food_date
        #                                                                       //ID of the food selected | ID of the current date where we are adding the food        
        db.execute('INSERT into food_date (food_id, log_date_id) values (?,?)',[request.form['food-select'],date_result['id']])
        db.commit()

    #================== Head tittle =========================
    #print('*********')
    #print(result['entry_date'])#20170123
    d = datetime.strptime(str(date_result['entry_date']),'%Y%m%d')
    prettyDate = datetime.strftime(d,'%B %d, %Y')
    #========================================================

    #=== To Fill drop down list =============================
    food_cur = db.execute('SELECT id, name FROM food')
    food_results = food_cur.fetchall()
    #======================================================== 

    #=== Get the specific food relationed with the date =====
    log_cur = db.execute('''SELECT food.name, food.protein, food.carbohydrates, food.fat, food.calories 
                            FROM log_date JOIN food_date ON food_date.log_date_id = log_date.id JOIN food ON food.id = food_date.food_id 
                            WHERE log_date.entry_date = ?''',[date])
    log_results = log_cur.fetchall() 

    #=== Get the totals =====================================
    #Dictionary
    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0 
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat'] 
        totals['calories'] += food['calories']


    return render_template('day.html',entry_date = date_result['entry_date'],prettyDate=prettyDate, food_results=food_results, log_results = log_results, totals=totals)

#================ FOOD ENDPOINT =================
@app.route('/food', methods=['GET', 'POST'])
def food_F():
    #Get a connection to the data base
    db = get_db()

    if request.method == 'POST':
        Food = request.form['FoodName']
        Protein = int(request.form['Protein'])
        Carbs = int(request.form['Carbohydrates'])
        Fat = int(request.form['Fat'])

        #Calculate calories
        calories = Protein * 4 + Carbs * 4 + Fat * 9
    
        #Write the sql sentence
        db.execute('INSERT INTO food (name,protein,carbohydrates,fat,calories) VALUES (?,?,?,?,?)',[Food,Protein,Carbs,Fat,calories])
        #Execute sql sentence
        db.commit()
    #Get the data, from the data base to display in the page
    cur = db.execute('SELECT name,protein,carbohydrates, fat, calories FROM food')
    results = cur.fetchall()

    return render_template('add_food.html',results = results)
    
if __name__ == '__main__':
    app.run(debug=True)
