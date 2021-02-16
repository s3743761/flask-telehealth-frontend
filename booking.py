import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session, Blueprint
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import requests
import os
import botocore
import string
import random
from cognito import cognitoRoute


APP_CLIENT_ID = "281hf825n7bh0t0s55giarg103"
dynamoRoute = Blueprint('dynamoRoute', __name__)

dynamodb = boto3.resource('dynamodb',  region_name='us-west-2')

@dynamoRoute.route('/create_booking', methods=['GET'])
def create_booking_page():
    return render_template('booking.html')

@dynamoRoute.route('/create_booking', methods=['POST','GET'])
def create_booking():
    if request.method == 'POST':

        letters = string.ascii_lowercase
        booking_id=  ''.join(random.choice(letters) for i in range(10)) 
        client_name = request.form['cl_name']
        client_email = request.form['cl_email']
        admin_email = request.form['adm_email']
        time = request.form['time']
        date = request.form['date']
        meeting_name = request.form['meeting_name']

        r = requests.post('https://1r77dpeab4.execute-api.us-west-2.amazonaws.com/dev/booking',
            headers={"Authorization": session['idToken']},
            json= {"booking_id":booking_id, "client_name":client_name, "client_email":client_email, "time":time, "meeting_name":meeting_name, "date":date })

        return redirect(url_for('cognitoRoute.admin_home'))

    return redirect(url_for('dynamoRoute.create_booking_page'))


@dynamoRoute.route('/booking', methods=['POST','GET'])
def get_bookings():
    r = requests.get('https://1r77dpeab4.execute-api.us-west-2.amazonaws.com/dev/booking',
    headers={"Authorization": session['idToken']})
    number_of_elements = r.json()['Count']

    
    client_email = []
    client_name = []
    date = []
    time = []
    booking_id = []
    meeting_name = []

    for i in range(number_of_elements):
        client_email.append(r.json()['Items'][i]['client_email'])
        client_name.append(r.json()['Items'][i]['client_name'])
        date.append(r.json()['Items'][i]['date'])
        time.append(r.json()['Items'][i]['time'])
        booking_id.append(r.json()['Items'][i]['booking_id'])
        meeting_name.append(r.json()['Items'][i]['meeting_name'])

    print(request.form.get("booking_id"))
    
    if r:
        return render_template("getbookings.html", emails = client_email, names = client_name, dates = date, times = time
        , booking_ids = booking_id, meeting_names = meeting_name )
    
    return render_template("getbookings.html")

@dynamoRoute.route('/delete_booking', methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        print('please_print')
        booking_id = request.form['booking_id']
        
        table = dynamodb.Table('Bookings')
        r = requests.delete('https://1r77dpeab4.execute-api.us-west-2.amazonaws.com/dev/delete_booking',
            headers={"Authorization": session['idToken']}, json= {"booking_id":booking_id})
        return redirect(url_for('cognitoRoute.admin_home'))
    return render_template("getbookings.html")

@dynamoRoute.route('/edit_booking', methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        print('h')
        client_name = request.form['client_name']
        client_email = request.form['client_email']
        date = request.form['date']
        time = request.form['time']
        meeting_name = request.form['meeting_name']
        booking_id = request.form['edit_booking_id']
        print(client_name)
        r = requests.post('https://1r77dpeab4.execute-api.us-west-2.amazonaws.com/dev/edit_booking',
            headers={"Authorization": session['idToken']},json= {"client_name":client_name,"date":date,"time":time,"client_email":client_email,"meeting_name":meeting_name,"booking_id":booking_id})
        print(r)
        return redirect(url_for('cognitoRoute.admin_home'))
    return render_template("getbookings.html")

@dynamoRoute.route('/client_bookings', methods=['POST','GET'])
def get_booking_for_user():

    r = requests.get('https://1r77dpeab4.execute-api.us-west-2.amazonaws.com/dev/client_booking',
            headers={"Authorization": session['idToken']})
    
    client_name = []
    date = []
    time = []
    booking_id = []
    meeting_name = []

    number_of_elements = r.json()['Count']

    for i in range(number_of_elements):
        client_name.append(r.json()['Items'][i]['client_name']['S'])
        date.append(r.json()['Items'][i]['date']['S'])
        time.append(r.json()['Items'][i]['time']['S'])
        booking_id.append(r.json()['Items'][i]['booking_id']['S'])
        meeting_name.append(r.json()['Items'][i]['meeting_name']['S'])
    
    
    return render_template("get_client_bookings.html", names = client_name, dates = date, times = time
        , booking_ids = booking_id, meeting_names = meeting_name)

