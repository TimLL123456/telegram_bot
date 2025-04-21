# Send message

1. Markdown Format
```python
user_input = request.get_json()
user_input_json = json.dumps(user_input, indent=4)

html_message = f"<pre>\n{user_input_json}\n</pre>"

url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

params = {
    "chat_id": 1174923863,
    "text": html_message,
    "parse_mode": "HTML"
}

response = requests.post(url, data=params)
```

2. Text Format
```python
message = "How are you"

url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

params = {
    "chat_id": 1174923863,
    "text": message,
}

response = requests.post(url, data=params)
```

# Set Command
1. Set Command
```python
# Set command
commands = [
    {"command": "start", "description": "Start the bot"},
    {"command": "help", "description": "Get help"}
]

# Telegram API URL for setMyCommands
url = f"https://api.telegram.org/bot{TG_API}/setMyCommands"
Parameters for the API request (serialize commands to JSON)
data = {
    "commands": json.dumps(commands)
}

# Send the request to Telegram API
response = requests.post(url, data=data)
```

2. Remove all Command
```python
# Set command
commands = []

# Telegram API URL for setMyCommands
url = f"https://api.telegram.org/bot{TG_API}/setMyCommands"
Parameters for the API request (serialize commands to JSON)
data = {
    "commands": json.dumps(commands)
}

# Send the request to Telegram API
response = requests.post(url, data=data)
```