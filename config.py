from dotenv import load_dotenv
import json
import os

from ngrok_executor import start_ngrok

load_dotenv()

WEBHOOK_HOST = start_ngrok()
TOKEN = os.environ.get("TOKEN")
WEBAPP_HOST = os.environ.get("WEBAPP_HOST")
WEBAPP_PORT = os.environ.get("WEBAPP_PORT")
WEBHOOK_URL = f"{WEBHOOK_HOST}telegram-webhook"
ADMIN_ID_LIST = json.loads(os.environ.get("ADMIN_ID_LIST"))
SUPPORT_LINK = os.environ.get("SUPPORT_LINK")
COMMUNITY_LINK = os.environ.get("COMMUNITY_LINK")
DB_NAME = os.environ.get("DB_NAME")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
PRODUCT_ID = os.environ.get("PRODUCT_ID")