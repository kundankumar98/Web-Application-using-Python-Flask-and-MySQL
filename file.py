import json
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from datetime import datetime, date


# import mysql.connector

app = Flask(__name__)

with open('C:/Users/Kundan/PycharmProjects/web/templates/config.json', 'r') as c:
    params = json.load(c)["params"]

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)

user_a = {"username_a": "admin", "password_a": "123"}


# user1 = {"username1": "tourist", "password1": "123"}
@app.route("/")
@app.route("/log", methods=['GET', 'POST'])
def log():
    msg = ''
    error = ''
    if request.method == 'POST':
        username_a = request.form.get('username_a')
        password_a = request.form.get('password_a')
        if username_a == user_a['username_a'] and password_a == user_a['password_a']:
            session['user_a'] = username_a
            return redirect('/indexAdmin')
        else:
            error = '  Invalid Credentials!'

    # if request.method == 'POST':
    #     username1 = request.form.get('username1')
    #     password1 = request.form.get('password1')
    #     if username1 == user1['username1'] and password1 == user1['password1']:
    #         session['user1'] = username1
    #         return redirect('/index1')
    #     else:
    #         error = '  Invalid Credentials!'

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect('/index1')
    else:
            msg = 'Incorrect username / password !'
            return render_template('log.html', msg=msg)

    return render_template('log.html', msg=msg, error=error, params=params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


# @app.route('/logout')
# def logout():
#     session.pop('userName')
#     return redirect(url_for('log.html'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/index1')
def home1():
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT  * FROM table_of_animals")
    data1 = cur1.fetchall()
    cur1.close()
    return render_template('index1.html', table_of_animals=data1, params=params)


@app.route('/indexAdmin')
def home():
    cur = mysql.connection.cursor()
    cur1 = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    cur3 = mysql.connection.cursor()
    cur.execute("SELECT  * FROM table_of_animals")
    cur1.execute("SELECT  * FROM table_of_rangers")
    cur2.execute("SELECT  * FROM table_of_caretakers")
    cur3.execute("SELECT  * FROM table_of_medics")
    data = cur.fetchall()
    data1 = cur1.fetchall()
    data2 = cur2.fetchall()
    data3 = cur3.fetchall()
    cur.close()
    return render_template('indexAdmin.html', table_of_animals=data, table_of_medics=data3, table_of_rangers=data1,
                           table_of_caretakers=data2, params=params)





@app.route("/about2", methods=['POST'])
def about2():
    zipcode = request.form['zip']
    r = requests.get('https://api.openweathermap.org/data/2.5/weather?zip='+zipcode+',in&appid=c4cc64ad1c968d36eee842968ce044cb')
    json_object = r.json()
    temp_k = float(json_object['main']['temp'])
    temp_f = int(temp_k - 273.15)

    humidity = int(json_object['main']['humidity'])
    speed = int(json_object['wind']['speed'])
    # main = (json_object['weather']['main'])
    country = (json_object['sys']['country'])
    pressure = (json_object['main']['pressure'])
    name = (json_object['name'])

    # today = date.today()
    today = datetime.today()

    
    return render_template('about2.html', temp=temp_f, humidity=humidity, speed=speed, country=country, pressure=pressure, name=name, today=today, params=params)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/team")
def team():
    cur1 = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    cur3 = mysql.connection.cursor()
    cur1.execute("SELECT  * FROM table_of_rangers")
    cur2.execute("SELECT  * FROM table_of_caretakers")
    cur3.execute("SELECT  * FROM table_of_medics")
    data1 = cur1.fetchall()
    data2 = cur2.fetchall()
    data3 = cur3.fetchall()
    cur1.close()
    return render_template('team.html', table_of_medics=data3, table_of_rangers=data1, table_of_caretakers=data2,
                           params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'phone' in request.form and 'message' in request.form:
        n = request.form['name']
        e = request.form['email']
        p = request.form['phone']
        m = request.form['message']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM contact WHERE Name = %s', (n,))
        if n == '' and p == '':
            msg = '*enter details !'
        else:
            cursor.execute('INSERT INTO CONTACT VALUES (NULL, %s, %s, %s, %s)', (n, e, p, m))
            mysql.connection.commit()
            msg = 'Submission Successful !!'
    elif request.method == 'POST':
        msg = 'please fill out the form !'
    return render_template('contact.html', params=params, msg=msg)


@app.route("/wildlife")
def our_reserves():
    return render_template('wildlife.html')


@app.route("/reg", methods=['GET', 'POST'])
def reg():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'phone' in request.form and 'address' in request.form:
        n1 = request.form['name']
        e1 = request.form['email']
        p1 = request.form['phone']
        a1 = request.form['address']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tourists WHERE Name = %s', (n1,))
        if n1 == '' and p1 == '':
            msg = '*enter details !'
        else:
            cursor.execute('INSERT INTO tourists VALUES (NULL, %s, %s, %s, %s)', (n1, e1, p1, a1))
            mysql.connection.commit()
            msg = 'Submission Successful !!'
    elif request.method == 'POST':
        msg = 'please fill out the form !'
    return render_template('reg.html', params=params, msg=msg)


#
# @app.route("/regAnimal", methods=['GET','POST'])
# def regAnimal():
#     msg=''
#     if request.method == 'POST' and 'Animal_id' in request.form and 'Name' in request.form and 'Population' in request.form and 'Order_name' in request.form and 'Genus_name' in request.form and 'Caretake_id' in request.form:
#         i1 = request.form['Animal_id']
#         n1 = request.form['Name']
#         e1 = request.form['Population']
#         p1 = request.form['Order_name']
#         a1 = request.form['Genus_name']
#         g1 = request.form['Caretaker_id']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM `table_of_animals` WHERE Name = %s', (i1,))
#         if (n1 == '' and e1 == ''):
#             msg='*enter details !'
#         else:
#             cursor.execute('INSERT INTO `table_of_animals` VALUES (NULL, %s, %s, %s, %s, %s)', (i1, n1, e1, p1, a1, g1))
#             mysql.connection.commit()
#             msg = 'Submission Successful !!'
#     elif request.method == 'POST':
#         msg = 'please fill out the form !'
#     return render_template('regAnimal.html', msg=msg)


@app.route('/services')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM tourists")
    data = cur.fetchall()
    cur.close()
    return render_template('services.html', students=data, params=params)


@app.route('/search', methods=['POST', 'GET'])
def search():
    mycursor = mysql.connection.cursor()
    # result = request.form
    if request.method == 'POST':
        result = request.form
        id = result['id']
        # mycursor.execute("SELECT * FROM `tourists` WHERE id=1")

        mycursor.execute("SELECT * FROM `tourists` WHERE id='" + id + "'")

        # mycursor.execute("SELECT * FROM `tourists` WHERE id = %s ", (id,))
        r = mycursor.fetchone()
        mycursor.close()
        return render_template('search.html', r=r)


@app.route('/searchAnimal', methods=['POST', 'GET'])
def search_animal():
    mycursor = mysql.connection.cursor()
    # result = request.form
    if request.method == 'POST':
        result = request.form
        name = result['name']
        # mycursor.execute("SELECT * FROM `tourists` WHERE id=1")

        mycursor.execute("SELECT * FROM `table_of_animals` WHERE name='" + name + "'")

        # mycursor.execute("SELECT * FROM `tourists` WHERE id = %s ", (id,))
        r = mycursor.fetchone()
        mycursor.close()
        return render_template('searchAnimal.html', r=r)


@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tourists WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('index'))




if __name__ == "__main__":
    app.run(debug=True)
