# -*- coding: utf-8 -*-
"""
    Loan Default Predictions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    An example web application for making predicions using a saved WLM model
    using Flask and the IBM WLM APIs.
    Created by Rich Tarro, modified by Dustin VanStee
    May 2017

    WML API : https://watson-ml-api.mybluemix.net/
"""

import os, urllib3, requests, json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify


creds = {
  "url": "https://ibm-watson-ml.mybluemix.net",
  "access_key": "kbXV3OOJ0i2mjGVhB461icjYpZlBFyiIjIpOn/ys0bSNe4rD50whFt1EcTocKgHvHxGxQ3pIogjgEOjN0TGDTcL0h32gVzPkwMbmHXNpi+FQYUqQmv73SQJrb1WXWeZv",
  "username": "7ddbfc51-2af5-4029-8e7f-f609a255fd5b",
  "password": "f5604e9e-7220-4f23-8a42-1ff814a72362",
  "instance_id": "d51854a2-84b2-41db-90f0-ac2419a944f2"
}


def get_token(creds):
    # This block gets your authorization token
    mltoken = 0
    headers = urllib3.util.make_headers(basic_auth='{}:{}'.format(creds["username"], creds["password"]))
    #url = '{}/v2/identity/token'.format(creds["url"])
    url = '{}/v3/identity/token'.format(creds["url"])
    response = requests.get(url, headers=headers)
    mltoken = json.loads(response.text).get('token')
    return mltoken


def score_example(creds, scoring_url, test_example_json) :

    # Get the scoring endpoint from the WML service
    #mltoken = get_token(creds)
    header_online = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + my_token}

    # API call here
    response_scoring = requests.post(scoring_url, data=test_example_json, headers=header_online)
    #print response_scoring.text
    return response_scoring.text




# One time fetch for these tokens at the start of the app
my_token = get_token(creds)


app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
))



@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


#http://localhost:6001/callwlm/1/1/1/1/1/1/1/1
#http://localhost:6001/callwlm/1/1.0/1.0/1.0/1.0/1.0/1.0/1
# Call lending club model 
# @app.route('/calllcm/<int:trips>/<float:mpt>/<float:avgsp>/<float:gt80pt>/<float:pwkd>/<float:pln>/<float:prh>/<int:nept>')
#def callwlm(trips,mpt,avgsp,gt80pt,pwkd,pln,prh,nept):

# model_type is either RF, or LR 
@app.route('/callwlm/<string:model_type>/<int:loan_amnt>/<int:annual_inc>/<float:dti>/<string:purpose>')
def callwlm(model_type,loan_amnt,annual_inc,dti,purpose):

    #print "Blank Slate ".format()
    
    sample_data = {
      "fields": ['LOAN_AMNT',
     'EMP_LENGTH',
     'VERIFICATION_STATUS',
     'HOME_OWNERSHIP',
     'ANNUAL_INC',
     'PURPOSE',
     'INQ_LAST_6MTHS',
     'OPEN_ACC',
     'PUB_REC',
     'REVOL_UTIL',
     'DTI',
     'TOTAL_ACC',
     'DELINQ_2YRS',
     'EARLIEST_CR_LINE',
     'ADDR_STATE',
     'TERM',
     'DEFAULT',
     'EMP_LISTED',
     'EMPTY_DESC',
     'EMP_NA',
     'DELING_EVER',
     'TIME_HISTORY'],
      "values": [
        [loan_amnt, '< 1 year', 'Source Verified', 'RENT', annual_inc, purpose, 1, 9, 0, 18.3, dti, 16, 0, 780969600000000000, 'CA', '36 months', 0, 1, 0, 0, 0, 6148, 0]
      ]
    }


    sample_json = json.dumps(sample_data)
    
    #DBG print " sample json" + sample_json

    # There is a programmatic way to get the url, but this is easy
    scoring_url = ""
    if(model_type == "LR") :
        scoring_url = 'https://ibm-watson-ml.mybluemix.net/v3/wml_instances/d51854a2-84b2-41db-90f0-ac2419a944f2/published_models/0c7052b8-fe40-49b1-8ce9-19a8ea964e99/deployments/da02c490-7aa6-44bb-854e-de85becea066/online'
    else :
        scoring_url = 'https://ibm-watson-ml.mybluemix.net/v3/wml_instances/d51854a2-84b2-41db-90f0-ac2419a944f2/published_models/5bfab4df-4343-4b11-a3f0-347730135a69/deployments/b64e9a5e-bfcf-45bc-8998-e9d915d50b4b/online'
    


    #print "model_type = " + model_type
    #print "scoring_url = " + scoring_url
    scoring_response = score_example(creds, scoring_url, sample_json)
    wml = json.loads(scoring_response)
    
    # First zip the fields and values together
    zipped_wml = zip(wml['fields'], wml['values'].pop())
    
    # Next iterate through items and grab the prediction value
    data = {
      'prediction' : "999",
      'probability' : "999"
    }


    data['prediction'] = [v for (k,v) in zipped_wml if k == 'prediction'].pop()
    data['probability'] = [v for (k,v) in zipped_wml if k == 'probability'].pop()[0]

    print "Default Prediction for this borrower is: " + str(data["prediction"])
    print "Default Probability for this borrower is: " + str(data["probability"])
    print "Returning \n" + str(data)
    return jsonify(data)

@app.route('/api/people/<name>')
def SayHello(name):
    message = {
        'message': 'Hello ' + name
    }
    return jsonify(results=message)

port = os.getenv('PORT', '6001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))



#   class Particle:
#   def __init__(self, mass, position, velocity, force):
#       self.mass = mass
#       self.position = position
#       self.velocity = velocity
#       self.force = force
