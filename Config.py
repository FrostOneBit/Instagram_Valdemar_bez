import os

from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv('TELEGRAM_TOKEN')
instagram_login = os.getenv("INSTAGRAM_LOGIN")
instagram_password = os.getenv("INSTAGRAM_PASSWORD")

Google_service_file = os.getenv("GOOGLE_SERVICE_FILE")
Google_table = os.getenv("GOOGLE_TABLE")
Google_donor = int(os.getenv("GOOGLE_DONOR"))
Google_reception = int(os.getenv("GOOGLE_RECEPTION"))

inst_login_button = ["Phone", "Телефон"]
inst_password_button = ["Password", "Пароль"]

database = os.getenv("DATABASE")

Geckodriver = "Firefox/Geckodriver/geckodriver.exe"
Profile_instagram = "Firefox/Profile"
Cookies = "Firefox/Cookies/inst_cookies"
