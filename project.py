from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash

)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Company, Employee
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "My-Item-Catalog"

UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Database and create database session
engine = create_engine('sqlite:///company.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print("welcome")
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url1 = 'https://graph.facebook.com/oauth/access_token?'\
        + 'grant_type=fb_exchange_token&'\
        + 'client_id=%s&client_secret=%s'\
        + '&fb_exchange_token=%s'
    url = url1 % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token \
        exchange we have to
        split the token first on commas and select the first index which\
         gives us the key : value
        for the server access token then we split it on colons to pull out \
        the actual token value
        and replace the remaining quotes with nothing so that it can be \
        used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url2 = 'https://graph.facebook.com/v2.8/me?access_token=%s&' \
        + 'fields=name,id,email'
    url = url2 % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token
    # Get user picture
    url3 = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&'\
        + 'redirect=0&height=200&width=200'
    url = url3 % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print(data)

    login_session['picture'] = data["data"]["url"]
    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: 150px;\
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# fb disconnect function to disconnect from fb login
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url1 = 'https://graph.facebook.com/%s/permissions?access_token=%s'
    url = url1 % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# gconnect function to connect via google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print("welcome")
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is\
         already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    print(login_session['access_token'])
    print(login_session['gplus_id'])

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    print(data)

    name = data['email'].split("@")
    login_session['username'] = name[0]
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
# to create new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# To get user Information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# To get users information
def getUserID(email):
        user = session.query(User).filter_by(email=email).one()
        session.commit()
        return user.id


# DISCONNECT - Revoke a current user's token and reset their login_session
# To disconnect from google login
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for \
        given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect/')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCompany'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCompany'))


# show all company users
@app.route('/users/')
def showUsers():
    user = session.query(User).all()
    return render_template('myusers.html', user=user)


# to show all users JSON file
@app.route('/users/JSON')
def showUsersJSON():
    user = session.query(User).all()
    return jsonify(user=[u.serialize for u in user])


# show all company names
@app.route('/')
@app.route('/company/')
def showCompany():
    company = session.query(Company).all()
    if 'username' not in login_session:
        return render_template('publicCompany.html', company=company)
    else:
        return render_template('company.html', company=company)


# JSON company objects
@app.route('/company/JSON')
def companyJSON():
    company = session.query(Company).all()
    return jsonify(company=[r.serialize for r in company])


# JSON employee objects
@app.route('/employee/JSON')
def employeeJSON():
    employee = session.query(Employee).all()
    return jsonify(employee=[r.serialize for r in employee])


# To show single JSON employee object
@app.route('/employee/<int:employee_id>/JSON')
def singleEmployeeJSON(employee_id):
    employee = session.query(Employee).filter_by(id=employee_id).one_or_none()
    if employee:
        return jsonify(employee.serialize)
    else:
        return "No such a Employee"


# To add new company
@app.route('/company/new', methods=['GET', 'POST'])
def newCompany():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['image']
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # add your custom code to check that the uploaded file is a \
        # valid image and not a malicious file (out-of-scope for this post)
        file.save(f)
        company = Company(
            name=request.form['name'], user_id=login_session['user_id'],
            picture="/static/" + file.filename)
        session.add(company)
        flash('New company %s Successfully Created' % company.name)
        return redirect(url_for('showCompany'))
    else:
        return render_template('newCompany.html')


# TO show all companies
@app.route('/company/<int:company_id>/')
@app.route('/company/<int:company_id>/menu/')
def showEmployee(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    creator = getUserInfo(company.user_id)
    employee = session.query(Employee).filter_by(
        company_id=company_id).all()
    session.commit()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicemployee.html',
                               employee=employee,
                               company=company,
                               creator=creator)
    else:
        return render_template('employee.html',
                               employee=employee,
                               company=company,
                               creator=creator)


# Edit a Company
@app.route('/company/<int:company_id>/edit/', methods=['GET', 'POST'])
def editCompany(company_id):
    editedCompany = session.query(
        Company).filter_by(id=company_id).one()
    session.commit()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCompany.user_id != login_session['user_id']:
        return flash("You are not authorised to edit this Company.Please \
        create your own company in order to edit")
        # "<script>function myFunction() {alert('You are not \
        # authorized to edit this Company. Please create your own company \
        # in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCompany.name = request.form['name']
            flash('Company name Successfully Edited %s' % editedCompany.name)
            return redirect(url_for('showCompany'))
    else:
        return render_template('editCompany.html', company=editedCompany)


# Delete a Company
@app.route('/company/<int:company_id>/delete/', methods=['GET', 'POST'])
def deleteCompany(company_id):
    companyToDelete = session.query(
        Company).filter_by(id=company_id).one()
    session.commit()
    if 'username' not in login_session:
        return redirect('/login')
    if companyToDelete.user_id != login_session['user_id']:
        return flash("You are not authorised to delete this Company.Please \
        create your own company in order to delete")
        # "<script>function myFunction() {alert('You are not authorized to\
        # delete this company. Please create your own company in \
        # order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        # directory="/home/mandar/Downloads/FSND-Virtual-Machine/vagrant/mandar/"\
        # + "My-Item-Catalog-Project"
        url = companyToDelete.picture.split("/")
        string = url[1] + "/" + url[2]
        os.remove(string)
        session.delete(companyToDelete)
        flash('%s Successfully Deleted' % companyToDelete.name)
        session.commit()
        return redirect(url_for('showCompany', company_id=company_id))
    else:
        return render_template('deleteCompany.html', company=companyToDelete)


# Add new Employee
@app.route('/company/<int:company_id>/menu/new/', methods=['GET', 'POST'])
def newEmployee(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    company = session.query(Company).filter_by(id=company_id).one()
    session.commit()
    if login_session['user_id'] != company.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
         to add Employee to this Company. Please create your own Company in \
         order to add Employee.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        file = request.files['image']
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # add your custom code to check that the uploaded file is a valid \
        # image and not a malicious file (out-of-scope for this post)
        file.save(f)
        company = session.query(Company).filter_by(id=company_id).one()
        newEmployee = Employee(name=request.form['name'],
                               dob=request.form['dob'],
                               email=request.form['email'],
                               contact=request.form['mob'],
                               address=request.form['address'],
                               picture="/static/" + file.filename,
                               company_id=company_id,
                               user_id=company.user_id)
        print(newEmployee)
        session.add(newEmployee)
        session.commit()
        flash('New Employee %s Successfully Added' % (newEmployee.name))
        return redirect(url_for('showEmployee', company_id=company_id))
    else:
        return render_template('newemployee.html', company=company)


# Edit a Employee
@app.route('/company/<int:company_id>/menu/<int:employee_id>/edit',
           methods=['GET', 'POST'])
def editEmployee(company_id, employee_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedEmployee = session.query(Employee).filter_by(id=employee_id).one()
    company = session.query(Company).filter_by(id=company_id).one()
    session.commit()
    if login_session['user_id'] != company.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit Employees to this company. Please create your own company\
         in order to edit employees.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedEmployee.name = request.form['name']
        if request.form['email']:
            editedEmployee.email = request.form['email']
        if request.form['dob']:
            editedEmployee.dob = request.form['dob']
        if request.form['address']:
            editedEmployee.address = request.form['address']
        if request.form['mob']:
            editedEmployee.contact = request.form['mob']
        session.add(editedEmployee)
        session.commit()
        flash('Employee Successfully Edited')
        return redirect(url_for('showEmployee', company_id=company_id))
    else:
        return render_template('editemployee.html',
                               company_id=company_id,
                               employee_id=employee_id,
                               employee=editedEmployee)


# Delete a Employee
@app.route('/company/<int:company_id>/menu/<int:employee_id>/delete',
           methods=['GET', 'POST'])
def deleteEmployee(company_id, employee_id):
    if 'username' not in login_session:
        return redirect('/login')
    company = session.query(Company).filter_by(id=company_id).one()
    session.commit()
    employeeToDelete = session.query(Employee).filter_by(id=employee_id).one()
    session.commit()
    if login_session['user_id'] != company.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete Employee to this company. Please create your own company \
        in order to delete Employees.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        url = employeeToDelete.picture.split("/")
        string = url[1] + "/" + url[2]
        os.remove(string)
        session.delete(employeeToDelete)
        session.commit()
        flash('Employee Successfully Deleted')
        return redirect(url_for('showEmployee', company_id=company_id))
    else:
        return render_template('deleteemployee.html',
                               employee=employeeToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
