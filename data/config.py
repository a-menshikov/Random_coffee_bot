from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TG_TOKEN')
ADMIN_TG_ID = os.getenv('ADMIN_TG_ID')
