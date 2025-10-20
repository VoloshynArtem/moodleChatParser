import subprocess
import requests
import json
import os
from dotenv import load_dotenv, dotenv_values 

load_dotenv() 

def message_flow(notification_level, message):
    #0 = os level only; 1 = os + discord level
    os_notification(message)
    if notification_level == 0: return
    discord_notification(message)



def os_notification(message):
    subprocess.run(["notify-send", "moodle chat parser" , message])# currently only KDE Plasma


def discord_notification(message):
    message = {"content": message}  

    response = requests.post(
        os.getenv("WEBHOOK_URL"), data=json.dumps(message),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 204:
        print(f"Failed to send message: {response.status_code}, {response.text}")
        