# import re
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv("TOKEN")

# with open(r"C:\Users\Lam\Desktop\Side Project\Telegram Bot Project\telegram_bot\Webhook_version\output.txt", "r",
#           encoding="utf-16-le") as file:
#     lines = file.readlines()

# pattern = "https://.*\.serveo.net"
# webhook_url = re.search(pattern, lines[0]).group()

# tg_webhook_api = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"

# response = requests.get(tg_webhook_api)
# print(response.text)

import re
import requests
import os
import subprocess
from dotenv import load_dotenv

# Load Telegram token from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ===== STEP 1: Run SSH command and capture output =====
def run_ssh_and_get_url():
    try:
        # Start SSH tunnel and capture output in real-time
        process = subprocess.Popen(
            ["ssh", "-R", "80:127.0.0.1:5000", "serveo.net"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,  # Ensure text mode
        )

        # # Read output line by line until URL is found
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())  # Print SSH output for debugging

            # Check if line contains Serveo URL
            match = re.search(r"https://.*\.serveo\.net", line)
            if match:
                webhook_url = match.group()
                return webhook_url

        raise RuntimeError("Serveo URL not found in SSH output.")

    except Exception as e:
        print(f"Error running SSH: {e}")
        exit(1)

# ===== STEP 2: Get the webhook URL from SSH =====
webhook_url = run_ssh_and_get_url()
print(f"\nExtracted URL: {webhook_url}")

# ===== STEP 3: Set up Telegram webhook =====
tg_webhook_api = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
response = requests.get(tg_webhook_api)
print("\nTelegram API Response:", response.text)

print("\n✅ Webhook setup complete! The SSH tunnel is running.")
print("Press Ctrl+C to stop the tunnel.")