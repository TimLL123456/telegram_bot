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

# Inline Keyboard Button
```python
message = "How are you"

url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

payload = {
        "chat_id": CHAT_ID,
        "text": "Choose an option:",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Option 1", "callback_data": "opt1"},
                    {"text": "Visit Google", "url": "https://google.com"}
                ]
            ]
        }
    }

# Send the request to Telegram API
response = requests.post(url, json=payload)
```

# LLM Reply Function
```python
def ai_response(user_input):
    """Function to get AI response from Deepseek API."""
    client = OpenAI(api_key=DEEPSEEK_API, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{user_input}"},
        ],
        stream=False
    )

    return response.choices[0].message.content

def index():
    if request.method == 'POST':

        ### Send message
        user_input = request.get_json()

        AI_reply = ai_response(user_input["text"])

        output_format = f"""
        User Input: {user_input}\n\n
        AI Reply: {AI_reply}
        """

        url = f"https://api.telegram.org/bot{TG_API}/sendMessage"

        params = {
            "chat_id": CHAT_ID,
            "text": output_format,
        }

        response = requests.post(url, data=params)

    return Response(status=200)
```