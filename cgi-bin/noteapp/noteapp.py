#import virtualenv python library directory
import os
import sys
sys.path.insert(0, '/var/www/clients/client6/web28/cgi-bin/venv/lib/python2.7/site-packages')


#import installed library
from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_moment import Moment
from datetime import datetime
#from flask_script import Manager
from flask_wtf import FlaskForm

#Import 3rd Party
from flask_mysqldb import MySQL
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SubmitField, IntegerField, HiddenField
from wtforms.validators import Required
from passlib.hash import sha256_crypt


#Third party imports
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

#Create application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is really hard to guess string'

# init Flask Bootstrap
bootstrap = Bootstrap(app)
moment = Moment(app)
admin = Admin(app)


#manager = Manager(app)


#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'c6noteapp'
#app.config['MYSQL_PASSWORD'] = 'imosudi@gmail.com'
app.config['MYSQL_PASSWORD'] = 'PASSWimosudi@gmail.co767868FFGFFDD#m'
app.config['MYSQL_DB'] = 'c6noteapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)


"""
python
from noteapp import db
db.create_all()

"""

from models import *


# Check user login status
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
	if 'logged_in' in session:
	    return f(*args, **kwargs)
	else:
	    flash(u'Unauthorized, Please login', 'danger')
	    return redirect(url_for('login'))
    return wrap


@app.route("/")
def home():
    pageName = "home"
    old_username = session.get('username')
    #app.logger.info(old_username)
    if old_username is None:
        return render_template("home.html", pageName=pageName, current_time=datetime.utcnow())
    else:
        return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    pageName = "about"
    return render_template("about.html", pageName=pageName, current_time=datetime.utcnow())
    pass


@app.route("/notes/create", methods=["GET", "POST"])
@is_logged_in
def create_note():
    pageName = "/notes/create"
    form = createNoteForm(request.form)
    if request.method == "POST" and  form.validate():
    	title = form.title.data
    	#notebody = form.notebody.data
    	body = form.body.data
        username = session['username']
        app.logger.info(username)

    	# Creating cursor
    	cur = mysql.connection.cursor()

    	cur.execute("INSERT INTO notes(title, body, username) VALUES(%s, %s, %s)", (title, body, username))

    	# Commit to Database
    	mysql.connection.commit()

    	#Close connection
    	cur.close()

    	flash(u"Note created and saved", "success")

    	return redirect(url_for('dashboard'))
    else:
        return render_template("create_note.html", form=form, pageName=pageName, current_time=datetime.utcnow())

@app.route("/notes/preedit/<string:id>", methods=['GET', 'POST'])
@is_logged_in
def note_preedit(id):
    pageName = "/notes/preedit"
    username = session['username']
    form = preEditNoteForm(request.form)
    note_id = form.note_id.data
    if request.method == "POST" and  form.validate() and id == note_id:
        return redirect(url_for('note_edit', id=id ))


# Edit notes
@app.route("/notes/edit/<string:id>", methods=["GET", "POST"])
@is_logged_in
def note_edit(id):
    pageName = "/notes/edit"
    username = session['username']
    if request.referrer != None:
        referrerurl = '/' + str((request.referrer).split('/')[-1])
        noteurl = '/' + str((request.referrer).split('/')[-1])
    else:
        flash(u"There is no need to be that smart!", "warning")
        return redirect(url_for('home'))
    app.logger.info(request.referrer)
    app.logger.info(referrerurl)
    app.logger.info(noteurl)
    app.logger.info(url_for('home'))
    if referrerurl == noteurl or request.referrer == url_for('dashboard') :
        app.logger.info('real request made')
        form = editNoteForm(request.form)
        #note_id = session['note_id']
        #app.logger.info(id)
        #app.logger.info(note_id)
        #author = session['author']
        #app.logger.info(author)

        if request.method == "POST" and  form.validate() :
            title = form.title.data
            body = form.body.data
            #author = form.author.data
            #app.logger.info(author)
            #username = session['username']
            #app.logger.info(username)

            # Creating cursor
            cur = mysql.connection.cursor()

            cur.execute("UPDATE notes SET title=%s, body=%s, username=%s WHERE id = %s", (title, body, username, [id]) )

            # Commit to Database
            mysql.connection.commit()

            #Close connection
            cur.close()

            flash(u"Note edited and saved", "success")

            return redirect(url_for('dashboard'))


        else:
            # Creating cursor
            cur = mysql.connection.cursor()

            #cur.execute("SELECT * FROM notes WHERE username = %s", [username] )

            cur.execute("SELECT * FROM notes WHERE id = %s", [id] )

            note = cur.fetchall()

            #app.logger.info(note)

            # Commit to Database
            mysql.connection.commit()

            #Close connection
            cur.close()

            #app.logger.info(username)


            #title = note['title']
            #body = note['body']


            return render_template("edit_note.html", form=form, pageName=pageName, note=note, id=id, current_time=datetime.utcnow())

    else:
        flash(u"Note edited impossible", "warning")
        return redirect(url_for('dashboard'))
    """
    form = createNoteForm(request.form)
    """

@app.route("/notes/delete/<string:id>", methods=['GET', 'POST'])
@is_logged_in
def note_delete(id):
    pageName = "/notes/delete"
    username = session['username']
    form = deleteNoteForm(request.form)
    if request.method == "POST" and  form.validate():
        note_id = form.note_id.data
        app.logger.info(note_id)
        app.logger.info(id)
        if id == note_id:
            cur = mysql.connection.cursor()

            # Not safe
            cur.execute("DELETE FROM notes WHERE id=%s", [id])

            # safe
            #noteDelInstruction = "DELETE FROM 'notes' WHERE id = ?"
            #cur.execute(noteDelInstruction, [id])

    	    # Commit to Database
            mysql.connection.commit()

            #Close connection
            cur.close()

            flash(u"Note Deleted !", "success")

            return redirect(url_for('home'))

    return redirect(url_for('home'))




"""
@app.route("/notes", methods=["GET", "POST"])
@is_logged_in
"""


@app.route('/register', methods=['GET', 'POST'])
def register():
    pageName= "/register"
    form = registrationForm(request.form)
    #form2 = registrationForm()
    #if form.method == 'POST' and  form.validate_on_submit():
    if request.method == 'POST' and  form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Creating cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s,	\
	 %s, %s,%s)", (name, username, email, password))

	    # Commit to Database
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash(u"Registration Complete, you may proceed to login", "success")

        return redirect(url_for('home'))

    else:
        return render_template('register.html', form=form, pageName=pageName,  current_time=datetime.utcnow())


# User login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = loginForm(request.form)
    pageName = "login"
    if request.method == 'POST': #and  form.validate():
	"""username = form.username.data
	password = sha256_crypt.encrypt(str(form.password.data))"""


	# login form data
	username = request.form['username']
	password_candidate = request.form['password']

	# login cursor
	cur = mysql.connection.cursor()

	# Getting looking up for the user in the database by username
	result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

	if result > 0:
	    #Extract hash
	    data = cur.fetchone()
	    password = data['password']
	    name = data['name'] #Fetching Name Details from Database

	    #Compare passwords
	    if sha256_crypt.verify(password_candidate, password):
		#Getting session details
		session['logged_in'] = True
		session['username'] = username
		session['name'] = name

		#app.logger.info('PASSWORD MATCHED')
		flash(u'Login successful', 'success')
		return redirect(url_for('dashboard'))

	    else:
		#app.logger.info('PASSWORD NOT MATCHED')
		error = 'Invalid login'
		return render_template('login.html', pageName=pageName, form=form, current_time=datetime.utcnow(), error=error)
	else:
	    #app.logger.info('NO USER FOUND')
	    error = 'Username not found'
	    return render_template('login.html', pageName=pageName, form=form, current_time=datetime.utcnow(), error=error)

    return render_template('login.html', pageName=pageName, form=form, current_time=datetime.utcnow())

# Application Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    pageName = "dashboard"

    # Fetching session['username']
    username = session['username']
    #app.logger.info(username)


    # Creating cursor
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM notes WHERE username = %s", [username])
    #result = cur.execute("SELECT * FROM notes ")
    app.logger.info(result)

    notes = cur.fetchall()

    #cur.execute("SELECT COUNT(*) FROM notes WHERE username = %s", [username])
    #countresult=cur.fetchone()
    #number_of_rows=countresult[0]
    #rownum=dict.values()[0]
    #app.logger.info(countresult)
    #app.logger.info(number_of_rows)
    #app.logger.info(rownum)


    if result > 0:
        return render_template('dashboard.html', result=result, pageName=pageName, notes=notes, current_time=datetime.utcnow())

    else:
        msg = "No Notes Found"
        return render_template('dashboard.html', pageName=pageName, msg=msg, current_time=datetime.utcnow())
    #return render_template('dashboard.html', pageName=pageName, current_time=datetime.utcnow())


# User Dashboard and Session
@app.route('/<username>/dashboard/')
@is_logged_in
def userDashboard(username):
    pageName = "userDashboard"
    username = session['username']
    return render_template('dashboard.html', pageName=pageName, username=username, current_time=datetime.utcnow())


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash(u"You are now logged out", "success")
    return redirect(url_for('login'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=datetime.utcnow()), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    #manager.run()
