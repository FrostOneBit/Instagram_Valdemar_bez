import os

from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv('TELEGRAM_TOKEN')
instagram_login = os.getenv("INSTAGRAM_LOGIN")
instagram_password = os.getenv("INSTAGRAM_PASSWORD")

database = os.getenv("DATABASE")