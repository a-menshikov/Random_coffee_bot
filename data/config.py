import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TG_TOKEN')
ADMIN_TG_ID = os.getenv('ADMIN_TG_ID')
