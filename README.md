## moodle chat parser
A simple Flask API to upload and parse chat HTML, extracting new messages from moodle (bcause i was bored)

## Features

- Accepts raw chat HTML via POST request on /upload-html
- Extracts message metadata using BeautifulSoup
- Saves output in multiple formats (for debugging for now)

### Output

- chat_list.html: Extracted chat section
- chat_list.json: Full parsed chat
- new_chat_list.json: Only new messages (compared to last run, may contain multiple items)
- ... more to come


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
```

### disable Observer by running
```
observer.disconnect();
```


## for now unrealized features
- send notifications through OS
- send notifications through Discord
- store messages in database ?
