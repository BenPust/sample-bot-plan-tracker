import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, url_for
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

bot_id = os.environ['BOT_ID']

@app.route('/', methods=['GET'])
def hello():
    return "Hello stranger! ;P"

@app.route('/', methods=['POST'])
def webhook():
    message = request.get_json()

    if not sender_is_bot(message):

        person = get_or_create(db.session, Person, name=message['name'])

        if intended_for_bot(message):
            if '\\bot hey' in message['text']: 
                reply_with_image('well done: big up', 'https://i.dailymail.co.uk/i/pix/2012/11/30/article-0-0B171630000005DC-93_306x423.jpg')
            elif '\\bot help' in message['text']:
                text = 'Hello!\nI save messages in a group chat and can get them when asked.\n\'\\bot show Ben Pust\' - will return all of the things Ben Pust has said.\nYou can also try \'\\bot hey\''
                reply(text)
            elif '\\bot show' in message['text']:
                s = message['text'].split()
                name_interest = s[s.index('show')+1] + " " + s[s.index('show')+2] # THIS IS BAD! :( just for not lol
                person_of_interest = db.session.query(Person).filter_by(name=name_interest).first()
                if person_of_interest:
                    persons_messages = db.session.query(Message).filter_by(owner_id=person_of_interest.id)
                    texts = str([x.string for x in persons_messages])
                    reply(texts)
                else:
                    reply("{} has not said anything".format(name_interest))
        else:
            # save what is said
            message_db_object = Message(string=message['text'],owner_id=person.id)
            db.session.add(message_db_object)
            db.session.commit()
            reply("...")
        

    return "OK", 200

# MARK: - helper methods

# MARK: DB
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

# MARK: parsing

def intended_for_bot(message):
    if '\\bot' in message["text"]:
        return True
    return False

# MARK: communication

# Send a message in the groupchat
def reply(msg):
	url = 'https://api.groupme.com/v3/bots/post'
	data = {
		'bot_id'		: bot_id,
		'text'			: msg
	}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()

# Send a message with an image attached in the groupchat
def reply_with_image(msg, imgURL):
	url = 'https://api.groupme.com/v3/bots/post'
	urlOnGroupMeService = upload_image_to_groupme(imgURL)
	data = {
		'bot_id'		: bot_id,
		'text'			: msg,
		'picture_url'		: urlOnGroupMeService
	}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()
	
# Uploads image to GroupMe's services and returns the new URL
def upload_image_to_groupme(imgURL):
	imgRequest = requests.get(imgURL, stream=True)
	filename = 'temp.png'
	postImage = None
	if imgRequest.status_code == 200:
		# Save Image
		with open(filename, 'wb') as image:
			for chunk in imgRequest:
				image.write(chunk)
		# Send Image
		headers = {'content-type': 'application/json'}
		url = 'https://image.groupme.com/pictures'
		files = {'file': open(filename, 'rb')}
		payload = {'access_token': 'eo7JS8SGD49rKodcvUHPyFRnSWH1IVeZyOqUMrxU'}
		r = requests.post(url, files=files, params=payload)
		imageurl = r.json()['payload']['url']
		os.remove(filename)
		return imageurl

# Checks whether the message sender is a bot
def sender_is_bot(message):
	return message['sender_type'] == "bot"

if __name__ == '__main__':
    app.run()