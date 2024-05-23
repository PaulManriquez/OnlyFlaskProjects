import sqlite3
from flask import Flask, g

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'SecretKeyPassword'

# Function to connect to the database
def connect_db():
    db_path = 'DataBasesFlask/data.db'
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
    return sql

# Function to get the database connection from the global context (g)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

# Teardown function to close the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Route to display results from the database
@app.route('/results')
def view_results():
    try:
        db = get_db()
        if db is None:
            return 'Unable to connect to the database'

        cur = db.execute('SELECT id, name, location FROM users')
        results = cur.fetchall()
        if results:
            result_str = '<h1>Database Content:</h1>'
            for row in results:
                result_str += f'<p>ID: {row["id"]} Name: {row["name"]} Location: {row["location"]}</p>'
            return result_str
        else:
            return 'No results found'
    except sqlite3.Error as e:
        return f'An error occurred: {str(e)}'

if __name__ == '__main__':
    app.run()