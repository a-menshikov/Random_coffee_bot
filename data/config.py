import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TG_TOKEN")
DB_DSN = os.getenv("DB_DSN")
ADMIN_TG_ID = os.getenv("ADMIN_TG_ID")
DEFAULT_PARE_iD = os.getenv("DEFAULT_PARE_iD")
DEFAULT_PARE_USERNAME = os.getenv("DEFAULT_PARE_USERNAME")
