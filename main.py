
import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import boto3
from botocore.exceptions import ClientError
import requests
import os
import botocore
from booking import dynamoRoute
from cognito import cognitoRoute
from s3 import s3Route

app = Flask(__name__)
APP_CLIENT_ID = "281hf825n7bh0t0s55giarg103"
app.config["IMAGE_UPLOADS"] = "static/img"
app.secret_key = '281hf825n7bh0t0s55giarg103'

app.register_blueprint(s3Route)
app.register_blueprint(cognitoRoute)
app.register_blueprint(dynamoRoute)

if __name__ == '__main__':
   
    app.run(debug=True)