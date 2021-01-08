import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
KEY_EGR = os.getenv('KEY_EGR')
KEY_BANK_INFO = os.getenv('KEY_BANK_INFO')
ADMIN_ID = os.getenv('ADMIN_ID').split()
SHEETS_ID = os.getenv('SHEETS_ID')
DATABASE =os.getenv('DATABASE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
