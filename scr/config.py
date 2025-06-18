import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from a .env file
load_dotenv()

# 1. Define all required environment variable keys and their values in a dictionary.
#    This makes them easy to check in a loop.
required_vars = {
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API"),
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY")
}

# 2. Use a list comprehension to find all keys whose values are None or empty.
#    This logic is inspired by the provided search result [1].
missing_vars = [key for key, value in required_vars.items() if not value]

# 3. If the list of missing variables is not empty, raise a specific error.
if missing_vars:
    # The error message now lists exactly which variables to check in your .env file.
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# If the check passes, you can assign the variables for use in your app
PERPLEXITY_API_KEY = required_vars["PERPLEXITY_API_KEY"]
TELEGRAM_BOT_TOKEN = required_vars["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = required_vars["TELEGRAM_CHAT_ID"]
SUPABASE_URL = required_vars["SUPABASE_URL"]
SUPABASE_KEY = required_vars["SUPABASE_KEY"]

# Note: Variables constructed from other variables (like TELEGRAM_API_URL)
# or client objects (like SUPABASE_CLIENT) should be defined after this check.
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
# SUPABASE_CLIENT = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

print("All required environment variables are set.")


# # Perplexity Keys
# PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API")

# # Telegram Configuration
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
# TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# # Supabase Configuration
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Ensure required variables are set
# if not all([
#     PERPLEXITY_API_KEY,
#     TELEGRAM_BOT_TOKEN,
#     TELEGRAM_CHAT_ID,
#     TELEGRAM_API_URL,
#     SUPABASE_URL,
#     SUPABASE_KEY,
#     SUPABASE_CLIENT
# ]):
#     raise ValueError("One or more required environment variables are not set.")