## moodle chat parser
A simple Flask API to upload and parse chat HTML, extracting new messages from moodle (bcause I was bored)

## Features
- Accepts raw chat HTML via POST request on /upload-html
- Extracts message metadata using BeautifulSoup
- Saves output in multiple formats (for debugging for now)

### Output
- messageflow 
    - os notifications (only tested with KDE Plasma for now)
    - discord notifications with webhooks  
- saving messages into db running in docker



## Usage

### Install dependencies:
```
pip install -r requirements.txt
```

### Run the server:
```
python main.py
```

### create a MutationObserver by runniong the following in your browser's console

```
const chatList = document.getElementById('chat-list');

if (chatList) {
    const observer = new MutationObserver((mutationsList) => {
        const hasRelevantChange = mutationsList.some(mutation => {
            return (
                mutation.type === 'childList' && (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0) ||
                mutation.type === 'characterData'
            );
        });

        if (hasRelevantChange) {
            fetch('http://localhost:5000/upload-html', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    html: document.documentElement.outerHTML
                })
            }).catch(console.error);
        }
    });

    observer.observe(chatList, {
        childList: true,
        subtree: true,
        characterData: true
    });
} else {
    console.warn('#chat-list not found in the DOM');
}
```

### disable Observer by running
```
observer.disconnect();
```

### seting up discord webhook
go to your server settings -> Integrations -> Webhooks -> craete new Webhook, set name and channel -> Copy Webhook url  
create .env file in project root directory  
format .env file to 
```
WEBHOOK_URL = "<webhook url copied from discord>"

ADMIN_USER = "<your postgres admin username>"   # usually postgres  
ADMIN_PASSWORD= "<your postgres admin password>"
NEW_USER  = "<your new postgres username>"
NEW_USER_PASSWORD = "<your new postgres user password>"
```


## for now unrealized/untested features
- refactor find new message to use db for lookup instead
- refactor message flow
- make everything a docker container 
- coloring messages in terminal output 