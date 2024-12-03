import os

from dotenv import load_dotenv
from webdriver_manager.drivers.firefox import GeckoDriver

load_dotenv()

telegram_token = os.getenv('TELEGRAM_TOKEN')
instagram_login = os.getenv("INSTAGRAM_LOGIN")
instagram_password = os.getenv("INSTAGRAM_PASSWORD")

inst_login_button = ["Phone", "Телефон"]
inst_password_button = ["Password", "Пароль"]

database = os.getenv("DATABASE")

Geckodriver = "Firefox/Geckodriver/geckodriver.exe"
Profile_instagram = "Profile"