from flask import Flask, render_template, request, session, redirect
from sqlalchemy import create_engine, MetaData, Column, Table, Integer, String
import json


# Initializes app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "Valley Children's :D"


# Initializes databases
patientData_engine = create_engine('sqlite:///patientData.db', echo = True)
patientData_meta = MetaData()
loginData_engine = create_engine('sqlite:///loginData.db', echo = True)
loginData_meta = MetaData()

patientData = Table(
   'patientData', patientData_meta,
   Column('id', Integer, primary_key = True),
   Column('name', String),
   Column('birthday', String))

loginData = Table(
   'loginData', loginData_meta,
   Column('id', Integer, primary_key = True),
   Column('username', String),
   Column('password', Integer))

patientData_meta.create_all(patientData_engine)
loginData_meta.create_all(loginData_engine)




# App responses to connections at various URLs

# Initialization at starting the program
@app.route('/')
def home():
    # Sets the current user to be null, displays login page
    session['username'] = "null"
    session['patient'] = "null";
    return render_template('index.html')




@app.route('/patientdata', methods = ['UPLOAD','PULLLIST', 'PULL'])
def patientDataFunction():
    if (request.method == 'UPLOAD'):
        return "User not found"
    if (request.method == 'PULLLIST'):
        # Probably add some kind of security for people just putting bs in
        patientData_connection = patientData_engine.connect()
        s = "SELECT * FROM patientData"
        result = patientData_connection.execute(s)

        # Creates string returnedPatientData to store patient data
        returnedPatientData = ''
        # Iterates through returned list using parameter row for each line
        for row in result:
            # Converts the row of data to a string
            string = str(row)
            # Cuts out unnecessary portions of the data
            string = string[string.index(',')+2:string.index(')')]
            # Appends data
            returnedPatientData += '{' + string + "}"


        patientData_connection.close()
        return returnedPatientData
    if (request.method == 'PULL'):
        # Probably add some kind of security for people just putting bs in
        return "null"


@app.route('/patients', methods = ['GET'])
def patientDisplayFunction():
    if session.get('username') is not None:
        if (session['username'] != "null"):
             return render_template('patients.html')
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/login', methods = ['PASS'])
def loginFunction():
    if (request.method == 'PASS'):
        loginData_connection = loginData_engine.connect()

        # Takes in username and password from the log-in page and assigns them to username and password
        loginForm = request.data
        loginForm = loginForm.decode()
        loginForm = json.loads(loginForm)
        username = str(loginForm['username'])
        password = loginForm['password']

        # Finds password in the database (hashed) and assigns it to matchingPass
        s = "SELECT password FROM loginData WHERE username='" + username + "'"
        result = loginData_connection.execute(s)
        matchingPass = str(result.fetchone())
        print(matchingPass)
        print(password)
        loginData_connection.close()



        if (matchingPass == "None"):
            return "fail"

        # Found a password: converting to int and displaying
        matchingPass = matchingPass[1:-2]
        matchingPass = int(matchingPass)


        # If the password matches, the below is executed to login the user
        if (password == matchingPass):
            session['username'] = username;
            return "correct"
        else:
            return "incorrect"

@app.route('/display/<patientID>', methods = ['GET'])
def displayFunction(patientID):
    if session.get('username') is not None:
        if (session['username'] != "null"):
            session['patient'] = patientID;
            return render_template('display.html')
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

# Start the app
if __name__ == '__main__':
    app.run()
