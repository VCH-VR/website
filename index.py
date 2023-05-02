from flask import Flask, render_template, flash, request, session, redirect
from flask_cors import CORS
from sqlalchemy import create_engine, MetaData, Column, Table, Integer, String
from werkzeug.utils import secure_filename
from matplotlib import pyplot as plt;
from pylab import genfromtxt;
import json
import os


# Initializes app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "Valley Children's :D"


api_v1_cors_config = {
  "origins": ["*"],
  "methods": ["OPTIONS", "GET", "POST", "PASS"]
}
CORS(app, resources={"/*": api_v1_cors_config})

UPLOAD_FOLDER = '/home/Undefined100/cse120/static/patientFiles/'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'png', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
@app.route('/', methods=['GET', 'POST'])
def home():
    # Sets the current user to be null, displays login page
    if request.method == 'GET':
        session['username'] = "null"
        session['patient'] = "null";
        return render_template('index.html')




@app.route('/patientdata', methods = ['PULLLIST', 'PULL'])
def patientDataFunction():
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


@app.route('/patients', methods = ['GET', 'POST'])
def patientDisplayFunction():
    if request.method == 'GET':
        if session.get('username') is not None:
            if (session['username'] != "null"):
                return render_template('patients.html')
            else:
                return render_template('index.html')
        else:
            return render_template('index.html')
    if request.method == 'POST':
        # check if the post request has the file part
        print("Test")
        if 'file' not in request.files:
            print("Test1")
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("Test2")
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            # Integrate the file ^^
            # Names MUST be MMDDYYYYPATIENT_NAME.txt
            filename = secure_filename(file.filename)
            filename = str(filename)
            birthday = filename[:8]
            patientName = filename[8:-4]

            # File is likely valid at this point, nothing bad will happen if the file makes it by here anyways - Enforce security later probably
            if (birthday.isdigit()):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                patientData_connection = patientData_engine.connect()

                s = "SELECT birthday FROM patientData WHERE name='" + patientName + "'"
                result = patientData_connection.execute(s)
                result = str(result.fetchone())
                if (str(birthday) == result[2:-3]):
                    print("Updated Patient Data")
                else:
                    print(result)
                    s = "INSERT INTO patientData (name, birthday) VALUES ('" + patientName + "', '" + birthday + "')"
                    patientData_connection.execute(s)
                patientData_connection.close()


                # Make the numpy graph
                plt.clf()
                plt.rcParams["figure.figsize"] = [7.00, 3.50]
                plt.rcParams["figure.autolayout"] = True

                filedata = genfromtxt(os.path.join(app.config['UPLOAD_FOLDER'], filename));
                leftEye = filedata[:, 0]
                rightEye = filedata[:, 1]
                leftEye = leftEye[leftEye != -1]
                rightEye = rightEye[rightEye != -1]

                plt.plot(leftEye, label="Left Eye");
                plt.plot(rightEye, label="Right Eye");


                plt.legend();
                plt.title(patientName.replace("_", " ") + "'s Eye Chart")
                plt.xlabel('Time')
                plt.ylabel('Milimeters')

                plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], filename[:-4] + ".png"))


            return render_template('patients.html')
        return "Bad File Type: {'txt', 'csv', 'json', 'png', 'jpg'} allowed"


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
        print("test")


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

@app.route('/display/<patient>', methods = ['GET'])
def displaySetter(patient):
    if session.get('username') is not None:
        if (session['username'] != "null"):
            session['patient'] = patient;
            return render_template('display.html')
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/display', methods = ['PULL'])
def displayGetter():
    if session.get('username') is not None:
        return session['patient']
    else:
        return ""


# File Input Handling

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






# Start the app
if __name__ == '__main__':
    app.run()
