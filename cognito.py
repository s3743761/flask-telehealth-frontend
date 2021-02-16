import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session, Blueprint
import boto3
from botocore.exceptions import ClientError
import requests
import os
import botocore


APP_CLIENT_ID = "281hf825n7bh0t0s55giarg103"

cognito_client = boto3.client('cognito-idp', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb',  region_name='us-west-2')
dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")

cognitoRoute = Blueprint('cognitoRoute', __name__)

send_email =''


@cognitoRoute.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')

@cognitoRoute.route('/contact_user', methods=['GET'])
def contact_page_user():
    return render_template('contact_user.html')

@cognitoRoute.route('/Adminhome', methods=['GET'])
def admin_home():
    return render_template('Adminhome.html')

@cognitoRoute.route('/Userhome', methods=['GET'])
def user_home():
    return render_template('home.html')

@cognitoRoute.route('/auth/signup', methods=['GET'])
def create_account():
    return render_template("create_account.html")

@cognitoRoute.route('/about', methods=['GET'])
def about_page():
    return render_template("about.html")

@cognitoRoute.route('/about_user', methods=['GET'])
def about_page_user():
    return render_template("about_user.html")

@cognitoRoute.route('/', methods=['GET'])
def login_page():
    return render_template("login.html")




@cognitoRoute.route('/auth/signup/', methods=['POST'])
def signup():
    if request.method == 'POST':
        user_email = request.form['Email']
        user_password = request.form['Password']
        user_name = request.form['Username']
        usertype = request.form['usertype']

        try:
            cognito_client.sign_up(ClientId=APP_CLIENT_ID,
                            Username=user_email,
                            Password=user_password,
                            UserAttributes=[{'Name': 'name', 'Value': user_name}])
        except ClientError as e:
            if e.response['Error']['Code'] == 'UsernameExistsException':
                
                print("User already exists")
                return redirect(url_for('cognitoRoute.create_account'))
            if e.response['Error']['Code'] == 'ParamValidationError':
                
                print("Param Validate Error")
                return redirect(url_for('cognitoRoute.create_account'))
            print(e)


        r = requests.post('https://xomyksdc28.execute-api.us-west-2.amazonaws.com/dev/add_usertype_profile',
        json= {"name":user_name,"email":user_email,"usertype":usertype})

        return redirect(url_for('cognitoRoute.login'))


    return redirect(url_for('cognitoRoute.create_account'))


@cognitoRoute.route('/auth/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['Email']
        password = request.form['Password']

        response = None
        
        global send_email
        


        try:
            response =  cognito_client.initiate_auth(ClientId=APP_CLIENT_ID,
                                        AuthFlow='USER_PASSWORD_AUTH',
                                        AuthParameters={
                                        'USERNAME': user_email,
                                        'PASSWORD': password
                                        }
            )
            session['idToken'] = response['AuthenticationResult']['IdToken']


            
            session['username'] = user_email


        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                
                print("Can't Find user by Email")
                return render_template("login.html", error = "Can't find user by email")
            if e.response['Error']['Code'] == 'ParamValidationError':
                
                print("Param Validate Error")
                return render_template("login.html", error = "Param Validate Error")

            if e.response['Error']['Code'] == 'NotAuthorizedException':
                print("Not Valid")
                # return redirect(url_for('cognitoRoute.login_page'))
                return render_template("login.html", error = "Wrong Email or Password")


        r = requests.get("https://8c7ymla190.execute-api.us-west-2.amazonaws.com/dev/test_auth", 
        headers={"Authorization": response['AuthenticationResult']['IdToken']})
        response_usertype = requests.get("https://xomyksdc28.execute-api.us-west-2.amazonaws.com/dev/profile", 
        headers={"Authorization": session['idToken']})
        print(response_usertype.json()['usertype'])
        session['token'] = response['AuthenticationResult']['AccessToken']
        print(session['idToken'])

        dynamo_userType = response_usertype.json()['usertype']
        print(dynamo_userType)

        if dynamo_userType == 'Normal':
            return redirect(url_for('cognitoRoute.user_home'))
        elif dynamo_userType == 'Admin':
            return redirect(url_for('cognitoRoute.admin_home'))
       
    return redirect(url_for('cognitoRoute.login_page'))

