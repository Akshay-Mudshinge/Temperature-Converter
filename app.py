from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    # Initialize the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS login_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()
    conn.close()

def view_table(table_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print(f"No data found in table '{table_name}'.")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

    conn.close()

def export_table_to_excel(table_name, filename):
    conn = sqlite3.connect('users.db')

    try:
        # Read table into a DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.to_excel(filename, index=False)
        print(f"Table '{table_name}' has been exported to '{filename}'.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()

@app.route('/')
def home():
    if 'user' in session:
        return f"Welcome {session['user']}! <a href='/logout'>Logout</a>"
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            # Log user login history
            cursor.execute('INSERT INTO login_history (username) VALUES (?)', (username,))
            conn.commit()
            conn.close()

            session['user'] = username
            return redirect('/')
        else:
            conn.close()
            return "User does not exist or incorrect credentials. <a href='/register'>Register here</a>."

    return '''
        <form method="POST">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            # Generate a unique ID for the new user (if needed, modify logic here for a custom ID format)
            cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return "Registration successful! <a href='/login'>Login here</a>."
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. <a href='/register'>Try again</a>."

    return '''
        <form method="POST">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Register</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/view_db/<table_name>')
def view_db(table_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            result = '<br>'.join([str(row) for row in rows])
        else:
            result = f"No data found in table '{table_name}'."

    except sqlite3.OperationalError as e:
        result = f"Error: {e}"

    conn.close()
    return f"<pre>{result}</pre>"

@app.route('/export_db/<table_name>', methods=['GET'])
def export_db(table_name):
    filename = f"{table_name}.xlsx"
    try:
        export_table_to_excel(table_name, filename)
        return f"Table '{table_name}' has been exported to '{filename}'. Check your project directory."
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
