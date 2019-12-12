from flask import Flask, request, redirect, url_for, session, render_template
from db import Database
app = Flask(__name__)

# App config
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey!'

# Init DB
db = Database('bettyDB.db')

@app.route('/')
def index():
    # If logged in, go to home page
    if session.get('username') is not None:
        return redirect(url_for('home', username=session['username']))
    # Not logged-in yet, go to login page
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'], defaults={'message':'Hello, please log-in'})
@app.route('/login/<message>', methods=['POST', 'GET'])
def login(message):
    # If already logged-in, go to home page
    if session.get('username') is not None:
        return redirect(url_for('home', username=session['username']))
    if request.method == 'POST':
        # Search for match in database
        for user in db.read('user', ('username', 'password')):
            if user[0] == request.form['username'] and user[1] == request.form['password']:
                session['username'] = user[0]
                return redirect(url_for('home'))
        # If none found
        return render_template('login.html', message='Invalid username and password')
    return render_template('login.html', message=message)

@app.route('/home')
def home():
    if session.get('username') is None:
        return redirect(url_for('login'))
    return render_template("home.html", username=session['username'], appeals=db.read('appeal'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    # If not logged in, go to login page
    if session.get('username') is None:
        return redirect(url_for('login'))
    # if form is submitted
    if request.method == "POST":
        for user in db.read(table='user', column=('username',)):
            if user[0] == request.form['username']:
                return render_template('register.html', message='Username already taken')
        if request.form['password'] != request.form['confirm_password']:
            return render_template("register.html", message='Please confirm the password correctly')
        username = request.form["username"]
        password = request.form["password"]
        db.create('user', ('username', 'password'), (username, password))
        return render_template('register.html', message='User created!')
    return render_template('register.html')

@app.route('/logout')
def logout():
    try:
        session.pop('username')
    except KeyError:
        return redirect(url_for('login'))
    return redirect(url_for('login', message='Logged out'))

@app.route('/edit_appeal', methods=['POST', 'GET'])
@app.route('/edit_appeal/<edit_id>', methods=['POST', 'GET'])
def edit_appeal(edit_id):
    if session.get('username') is None:
        return redirect(url_for('login')) #if not logged in, go to home page
    if request.method == 'POST': #get columns and values from form
        column, values = [], []
        for col, new_val in request.form.items():
            column.append(col)
            values.append(new_val)
        db.update('appeal', edit_id, column, values)
    results = db.read('appeal', where=(('id', edit_id),))
    return render_template('edit_appeal.html', appeal=results[  0], username=session['username'])

@app.route('/delete_appeal/<edit_id>')
def delete_appeal(edit_id):
    if session.get('username') is None:
        return redirect(url_for('login'))
    db.delete('appeal', edit_id)
    return redirect(url_for('home', username=session['username']))

@app.route('/add_appeal', methods=['POST', 'GET'])
def add_appeal():
    if session.get('username') is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        column, values = [], []
        for col, val in request.form.items():
            if val == '' or ((col == 'date_filed' or col == 'date_received') and val == 'dd/mm/yyyy'):
                return render_template('add_appeal.html', username=session['username'],
                                       message='Fill up all the fields')
            column.append(col)
            values.append(val)
        db.create('appeal', column, values)
        return redirect(url_for('home'))
    return render_template('add_appeal.html', username=session['username'])

@app.route('/delete_all')
def delete_all():
    if session.get('username') is None:
        return redirect(url_for('login'))
    db.delete('appeal') #since no edit_id, delete all records on appeal
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run()