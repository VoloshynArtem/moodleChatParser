from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

import json 
from chat_parser import parse_chat_html_to_json
from message_flow import *
from database import *
import logging

log = logging.getLogger('werkzeug')
log.disabled = True

app = Flask(__name__)
CORS(app)

lastKnownUsername = ""
last_messages = []

def find_new_messages(messages):
    global last_messages
    new_msgs = []

    if (len(last_messages) == 0): # handle first message after restart 
        last_messages = messages.copy()
        return [last_messages[-1]]
    
    for msg in reversed(messages):# workaround for not checking all messages, alternatively working closer with db 
        if msg.get("message_id") not in [m.get("message_id") for m in last_messages]:
            new_msgs.append(msg)
            last_messages.append(msg)
        else:
            break

    return new_msgs



def chat_div_found(chat_div):
    for msg in find_new_messages(parse_chat_html_to_json(chat_div)):
        message_flow(1,f"{msg.get("username")} =>> {msg.get("message")}")
        save_to_databese(msg)


def save_to_databese(msg):
    for atr in msg:        
        insert_chat(
            msg.get("message_id"),
            msg.get("username"),
            msg.get("message"),
            msg.get("time")
        )



@app.route('/upload-html', methods=['POST'])
def upload_html():
    data = request.get_json()
    full_html = data.get('html')

    soup = BeautifulSoup(full_html, 'html.parser')
    chat_div = soup.find('div', id='chat-list')


    if chat_div:
        chat_div_found(str(chat_div))

        return jsonify({"status": "success", "message": "chat-list saved."})
    else:
        return jsonify({"status": "error", "message": "chat-list not found"}), 404

if __name__ == '__main__':
    init_database()
    app.run(debug=True)

