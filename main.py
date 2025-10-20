from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import re
import json 
from chat_parser import parse_chat_html_to_json

app = Flask(__name__)
CORS(app)

lastKnownUsername = ""
last_messages = []

def find_new_messages(messages):
    global last_messages
    new_msgs = []

    if (len(last_messages) == 0): # handle first message restart start
        last_messages = messages.copy()
        return last_messages[-1]
    
    for msg in messages:
        if msg not in last_messages:
            new_msgs.append(msg)
            last_messages.append(msg)

    return new_msgs



def chat_div_found(chat_div):
    with open('chat_list.html', 'w', encoding='utf-8') as f:
        f.write(chat_div)

    with open('chat_list.json', 'w', encoding='utf-8') as f:
        json.dump(parse_chat_html_to_json(chat_div), f, ensure_ascii=False, indent=2)

    with open('new_chat_list.json', 'w', encoding='utf-8') as f:
        m = find_new_messages(parse_chat_html_to_json(chat_div))
        json.dump(m, f, ensure_ascii=False, indent=2)
        print(m)
        


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
    app.run(debug=True)



