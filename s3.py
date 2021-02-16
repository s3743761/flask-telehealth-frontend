
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session, Blueprint
import boto3
from botocore.exceptions import ClientError
import requests
from PIL import Image
import os
import botocore

client = boto3.client('s3', region_name='us-west-2')
s3_client = boto3.client('s3', region_name='us-west-2')
cognito_client = boto3.client('cognito-idp', region_name='us-west-2')

APP_CLIENT_ID = "281hf825n7bh0t0s55giarg103"
config = "static/img"

s3Route = Blueprint('s3Route', __name__)

dbName = ''
dbContact = ''

logged_username = ''
logged_password = ''



@s3Route.route('/profile', methods=['GET','POST'])
def profile():
    print(session['idToken'])
    # os.remove(os.path.join(app.config["IMAGE_UPLOADS"], str(session['username'])+".png"))
    r = requests.get("https://xomyksdc28.execute-api.us-west-2.amazonaws.com/dev/profile", 
    headers={"Authorization": session['idToken']})
    dynamo_userType = r.json()['usertype']
    print(dynamo_userType)

    global dbName 
    global dbContact 

    session['name'] = r.json()['name']
    session['contact'] = r.json()['contact']
    url = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': 'profilebucket',
                                    'Key': r.json()['email']+".png",
                                },                                  
                                ExpiresIn=3600)
    print(url)

    if dynamo_userType == "Admin":
        return render_template('profile.html',name = r.json()['name'],contact = r.json()['contact'],email = r.json()['email'], password = r.json()['password'],user_image = url)
    elif dynamo_userType == "Normal":
        return render_template('user_profile.html',name = r.json()['name'],contact = r.json()['contact'],email = r.json()['email'], password = r.json()['password'],user_image = url)

    return " "


@s3Route.route('/get-items')
def get_items():
    return jsonify(aws_controller.get_items())



@s3Route.route('/edit_profile',methods=['GET','POST'])
def editProfile():
    if request.method  == 'POST':
        print("h")
        print("I am INSIDIIEIIEIEI")
        name = request.form['name']
        # email = request.form['email']
        contact = request.form['contact']
        # password = request.form['password']
        if request.files:
        
            image = request.files["image"]
            print(session['username'])
            image.save(os.path.join(config, str(session['username'])+".png"))
   
            
            try:

                
                path = config+"/"+str(session['username'])+".png"
                print(image)
                print(str(session['username']))
                if image.filename != '':
                    # image_exists(str(session['username']))
                    s3_client.upload_file(str(path), 'profilebucket', str(session['username'])+".png")
                # else:
                #     response = s3_client.upload_file(str(path), 'profilebucket', str(session['username'])+".png")
            except ClientError as e:
                print(e)
                print("no")
                return None
        os.remove(os.path.join(config, str(session['username'])+".png"))
        r = requests.post('https://xomyksdc28.execute-api.us-west-2.amazonaws.com/dev/profile',
        headers={"Authorization": session['idToken']},json= {"name":name,"contact":contact})

        return redirect(url_for('s3Route.profile'))

     


    return render_template('edit_profile.html', name = session['name'], password = "password", email = "email", contact =  session['contact'])

@s3Route.route('/change_password',methods=['GET','POST'])
def change_password():
    if request.method == 'POST':
        previous_password = request.form['previous_password']
        new_password = request.form['new_password']
        try:
            
            response = cognito_client.change_password(
                PreviousPassword=previous_password,
                ProposedPassword=new_password,
                AccessToken=session['token']
            )

        except ClientError as e:
            if e.response['Error']['Code'] == 'ParamValidationError':
                print("Param Validate Error")
                return redirect(url_for('s3Route.profile'))

        return profile()
    return redirect(url_for('s3Route.profile'))

def createBucket():
   
    
    try:

        response = client.create_bucket(
        Bucket='profilebucket',
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2',
        },)
        
        print(response)

    except ClientError as e:
        print(e)
        print("no")
        
    return None

def download_image(name):
    s3 = boto3.resource('s3')
    path = config+"/"+str(name)+".png"
    s3.meta.client.download_file('profilebucket', name+".png", path)

def image_exists(name):
   
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3', region_name='us-west-2')
    path = config+"/"+str(session['username'])+".png"
    try:
        s3.Object('profilebucket', str(name)+".png").load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
     
            
            s3_client.upload_file(str(path), 'profilebucket', str(session['username'])+".png")
            print("not")
            return 
        else:
       
            print("g")

    print("exsists")
 
    
