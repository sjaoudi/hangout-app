import os
from flask import Flask, jsonify, request
from faker import Factory
from twilio.access_token import AccessToken, VideoGrant
from dotenv import load_dotenv, find_dotenv
import transcribe_streaming
from threading import Thread
from multiprocessing import Process, Queue
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
fake = Factory.create()
load_dotenv(find_dotenv())

socketio = SocketIO(app)

phrase_dict = dict()

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

# @app.route('/phrase')
# def getPhrase():
#     with open('test.txt', 'r') as f:
#         phrase = f.read()
#     return phrase

@socketio.on('my_event', namespace='/test')
def test_message(message):
    # print arg
    # emit('my_response', {'data': 'from the server'} )
    with open('test.txt', 'r') as f:
        phrase = f.read()
    emit('my_response', {'data': phrase})
    # emit('my_response', {'data': message['data']})

if __name__ == '__main__':
    # app.config['SERVER_NAME'] = 'localhost:8000'
    # app.run()
    # p1 = Process(target=app.run, args=())
    # socketio.run(app)
    p1 = Process(target=socketio.run, args=(app,))
    p1.start()
    while 1:
        q = Queue()
        p2 = Process(target=transcribe_streaming.main, args=(q,))
        p2.start()
        phrase = q.get()
        print 'phrase: ', phrase
        with open('test.txt', 'w') as f:
            f.write(phrase)
        p2.terminate()

    p2.join()
    p1.join()
