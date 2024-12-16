import os
import shutil
import asyncio

from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from Database import connect_to_database
from Get_cookies import main_get_cookies

from Config import (
    instagram_login,
    instagram_password,
    inst_login_button,
    inst_password_button,
    Profile_instagram,
    Geckodriver
)

async def create_profile_and_login_instagram():
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
        options.add_argument("--headless")
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
            print(f"ERROR: Кнопка 'Сохранить данные для входа' не найдена")

        print("SUCCESS: Авторизация завершена.")
        return True

    except Exception as ex:
        print(f"ERROR: Ошибка: {ex}")
    finally:
        driver.quit()
        print("INFO: Браузер закрыт.")

        await main_get_cookies() #Получение Cookies

async def insert_or_update_link(donor, link, post_date, post_date_add, caption, views, likes, comments, reposts):
    try:
        # Подключаемся к базе данных
        connect, cursor = await connect_to_database()

        current_date = datetime.now()

        # Проверяем, существует ли ссылка в базе данных
        cursor.execute("SELECT * FROM Links WHERE _link = ?", (link,))
        existing_link = cursor.fetchone()

        if existing_link:
            # Если ссылка уже существует, проверяем дату добавления
            date_added = datetime.strptime(existing_link[4],"%Y-%m-%d %H:%M:%S")  # _data_add в формате "YYYY-MM-DD HH:MM:SS"

            if current_date - date_added > timedelta(days=10):
                # Если прошло более 10 дней, удаляем запись
                cursor.execute("DELETE FROM Links WHERE _link = ?", (link,))
                print(f"Запись для {link} удалена, так как она старше 10 дней.")
            else:
                # Если прошло менее 10 дней, обновляем информацию
                cursor.execute(
                    """
                    UPDATE Links
                    SET _likes = ?, _views = ?, _count_comments = ?, _reposts = ?
                    WHERE _link = ?
                    """,
                    (likes, views, comments, reposts, link)
                )
                print(f"Данные для {link} обновлены.")
        else:
            # Если ссылки нет, добавляем новую запись
            cursor.execute(
                """
                INSERT INTO Links (_author, _link, _date_reels, _data_add, _caption, _views, _likes, _count_comments, _reposts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (donor, link, post_date, post_date_add, caption, views, likes, comments, reposts)
            )
            print(f"Новая запись добавлена для {link}. В Database")

    except Exception as ex:
        print(f"ERROR | Ошибка при работе с базой данных: {ex}")
    finally:
        connect.commit()
        cursor.close()
        connect.close()

async def insert_add_or_update_followers(donor, followers):
    try:
        # Подключение к базе данных
        connect, cursor = await connect_to_database()

        # Проверяем, существует ли уже запись для данного автора
        cursor.execute("SELECT _followers FROM Donors WHERE _donor = ?", (donor,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Если запись существует, обновляем количество подписчиков и время
            cursor.execute(
                """
                UPDATE Donors
                SET _followers = ?, _last_updated = CURRENT_TIMESTAMP
                WHERE _donor = ?
                """,
                (followers, donor)
            )
            print(f"Обновлено количество подписчиков для {donor}: {followers}")
        else:
            # Если записи нет, добавляем новую
            cursor.execute(
                """
                INSERT INTO Donors (_donor, _followers)
                VALUES (?, ?)
                """,
                (donor, followers)
            )
            print(f"Добавлена новая запись для {donor}: {followers}")

        # Сохраняем изменения
        connect.commit()

    except Exception as ex:
        print(f"ERROR | database_add_or_update_followers: {ex}")

    finally:
        connect.close()
