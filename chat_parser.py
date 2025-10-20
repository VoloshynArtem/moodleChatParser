### this is entirely vibe coded, so if you want to optimize this go ahead

from bs4 import BeautifulSoup

# Extract username structurally
def extract_username_from_container(container):
    msg_content = container.find('div', class_='chat-message-content')
    if not msg_content:
        return None

    outer_wrapper = msg_content.find_parent('div', class_='sc-cIAbwb')
    if not outer_wrapper:
        return None

    list_item = outer_wrapper.find('div', {'role': 'listitem'})
    if not list_item:
        return None

    username_div = list_item.find('div')
    if not username_div:
        return None

    return username_div.get_text(strip=True)[:-5]


def parse_chat_html_to_json(html: str):
    """
    Parse chat HTML and extract structured messages with username, message, time, and message_id.

    Returns:
        List[Dict[str, str]]: A list of message dictionaries.
    """
    soup = BeautifulSoup(html, "html.parser")
    chat_data = []
    lastKnownUsername = None

    chat_list = soup.find('div', id='chat-list') or soup

    message_containers = chat_list.find_all(
        lambda tag: tag.name == 'div' and tag.has_attr('class') and any('chat-message-container' in c for c in tag['class'])
    )

    for container in message_containers:
        # Extract message ID
        msg_content = container.find(lambda t: t.has_attr("data-chat-message-id"))
        message_id = msg_content.get("data-chat-message-id") if msg_content else None

        # Extract message text
        msg_el = container.find(attrs={"data-test": "messageContent"})
        message = msg_el.get_text(separator=" ", strip=True) if msg_el else ""

        

        username = extract_username_from_container(container)
        if username:
            lastKnownUsername = username
        else:
            username = lastKnownUsername

        # Extract time
        time_tag = container.find("time")
        time = time_tag.get_text(strip=True) if time_tag else None

        chat_data.append({
            "message": message,
            "username": username,
            "time": time,
            "message_id": message_id
        })

    return chat_data

