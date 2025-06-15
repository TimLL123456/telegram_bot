# Setup Serveo.net webhook and expose localhost server to internet

1. **Run flask app to host local server**

```python
import os
from dotenv import load_dotenv
from flask import Flask, Response, request

load_dotenv()
CMC_API = os.getenv("COINMARKETCAP_API")
TG_API = os.getenv("TOKEN")

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return Response("ok", status=200)

    return "<h1>Hello, World!</h1>"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

2. Run serveo.net command
* expose localhost server to the internet
```bash
PS C:\Users> ssh -R 80:127.0.0.1:5000 serveo.net
Forwarding HTTP traffic from https://84b98161c0dc999ef1c8a8aee9342f53.serveo.net
```

3. Setup telegram webhook url
setup_url = https://api.telegram.org/bot7879762613:AAFLGGOSyXpaGJWWnzTjt7A6lz0JYX4p7EY/setWebhook?url=https://84b98161c0dc999ef1c8a8aee9342f53.serveo.net/

* copy the setup_url to the browser