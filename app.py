import os
from flask import Flask, jsonify, request, Response, escape
from faker import Factory
from twilio.access_token import AccessToken, VideoGrant
from dotenv import load_dotenv, find_dotenv
import transcribe_streaming
from threading import Thread
from multiprocessing import Process, Queue
from flask.ext.socketio import SocketIO, emit
import time
import subprocess

app = Flask(__name__)
fake = Factory.create()
load_dotenv(find_dotenv())

#socketio = SocketIO(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/token')
def token():
    # get credentials for environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY']
    api_secret = os.environ['TWILIO_API_SECRET']

    # Create an Access Token
    token = AccessToken(account_sid, api_key, api_secret)

    # Set the Identity of this token
    token.identity = fake.user_name()

    # Grant access to Video
    grant = VideoGrant()
    grant.configuration_profile_sid = os.environ['TWILIO_CONFIGURATION_SID']
    token.add_grant(grant)

    # Return token info as JSON
    return jsonify(identity=token.identity, token=token.to_jwt())


# @app.route('/yield')
# def index1():
#     def stream(generator):
#         """Preprocess output prior to streaming."""
#         for line in generator:
#             yield escape(line.decode('utf-8'))  # Don't let subproc break our HTML
#
#     def test():
#         print "Test"
#
#     def inner():
#         q = Queue()
#         proc = subprocess.Popen(
#             test(),             #call something with a lot of output so we can see it
#             shell=True,
#             stdout=subprocess.PIPE
#         )
#
#         generator = stream(iter(proc.stdout.readline, b''))
#         return Response(generator, mimetype='text/html')
#
#         # for x in range(100):
#             # time.sleep(1)
#             # yield '%s<br/>\n' % x

@app.route('/phrase')
def getPhrase():
     #with open('test.txt', 'r') as f:
     phrase = "This is a random sentence"
     return phrase

@app.route('/yield')
def test_message():
    string = ''
    f =  open('test_1.txt', 'r')
    for line in f:
       string += line + "\r\n"

    return string

if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'localhost:8000'
    #app.run()
    p1 = Process(target=app.run, args=())
    p1.start()



    while 1:

        q = Queue()
        p2 = Process(target=transcribe_streaming.main, args=(q,))
        p2.start()
        phrase = q.get()

        print 'phrase: ', phrase
        p2.terminate()
        f = open('test_1.txt', 'a')
        f.write(phrase + "\n")
        

    p2.join()
    p1.join()
