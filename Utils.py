import os
import shutil
import asyncio

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from Config import (
    instagram_login,
    instagram_password,
    inst_login_button,
    inst_password_button,
    Profile_instagram,
    Geckodriver
)

async def create_profile_and_login_instagram(path):
    try:
        print("=== Начало создания профиля и авторизации в Instagram ===")

        # Создание профиля Firefox
        print("INFO: Создание профиля Firefox...")
        profile_path = os.path.abspath(Profile_instagram)
        if os.path.exists(profile_path):
            print("INFO: Папка профиля существует. Удаляем старую папку...")
            shutil.rmtree(profile_path)
        os.makedirs(profile_path)
        print(f"SUCCESS: Папка профиля создана: {profile_path}")

        # Настройка опций Firefox
        print("INFO: Настройка параметров браузера Firefox...")
        options = Options()
        options.add_argument("-profile")
        options.add_argument(profile_path)
        options.add_argument("--headless")  # Уберите, если хотите видеть браузер
        print("SUCCESS: Параметры Firefox настроены.")

        # Запуск браузера
        print("INFO: Запуск браузера Firefox...")
        service = Service(Geckodriver)
        driver = webdriver.Firefox(service=service, options=options)
        print("SUCCESS: Firefox успешно запущен.")

        # Переход на сайт Instagram
        print("INFO: Открытие сайта Instagram...")
        driver.get("https://www.instagram.com")
        await asyncio.sleep(3)
        print("SUCCESS: Сайт Instagram открыт.")

        # Поиск поля логина
        print("INFO: Поиск поля для ввода логина...")
        login_found = False
        for login_text in inst_login_button:
            try:
                login_field = driver.find_element(By.XPATH, f"//input[@name='username' or contains(@placeholder, '{login_text}')]")
                login_field.send_keys(instagram_login)
                login_found = True
                print("SUCCESS: Поле логина найдено и заполнено.")
                break
            except:
                continue
        if not login_found:
            print("ERROR: Поле логина не найдено.")
            driver.quit()
            return

        # Поиск поля пароля
        print("INFO: Поиск поля для ввода пароля...")
        password_found = False
        for password_text in inst_password_button:
            try:
                password_field = driver.find_element(By.XPATH, f"//input[@name='password' or contains(@placeholder, '{password_text}')]")
                password_field.send_keys(instagram_password)
                password_found = True
                print("SUCCESS: Поле пароля найдено и заполнено.")
                break
            except:
                continue
        if not password_found:
            print("ERROR: Поле пароля не найдено.")
            driver.quit()
            return

        # Нажимаем Enter для входа
        password_field.send_keys(Keys.RETURN)
        print("INFO: Выполняется вход в Instagram...")
        await asyncio.sleep(5)

        # Ожидание кнопки "Сохранить данные"
        try:
            print("INFO: Ожидание кнопки 'Сохранить данные для входа'...")
            wait = WebDriverWait(driver, 10)
            save_info_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Сохранить данные') or contains(text(), 'Save info')]")))
            save_info_button.click()
            print("SUCCESS: Кнопка 'Сохранить данные для входа' нажата.")
        except Exception as ex:
            print(f"ERROR: Кнопка 'Сохранить данные для входа' не найдена: {ex}")

        print("SUCCESS: Авторизация завершена.")

    except Exception as ex:
        print(f"ERROR: Ошибка: {ex}")
    finally:
        driver.quit()
        print("INFO: Браузер закрыт.")