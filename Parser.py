import asyncio
import instaloader

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from Utils import (
    create_profile_and_login_instagram,
    insert_or_update_link,
    insert_add_or_update_followers
)

from Utils_GoogleSheets import (
    google_sheet_read_donor,
    google_sheet_add_reception,
    google_sheet_add_followers
)

from Config import (
    Profile_instagram,
    Geckodriver,
    instagram_login,
    Cookies
)

#Запуск вех функция по парсингу
async def launch_parsing():
    try:
        bool_auth_instagram = await create_profile_and_login_instagram() #Создание профиля instagram
        status_data_donor, data_donor = await google_sheet_read_donor() #чтение reels

        if bool_auth_instagram and status_data_donor:
            reels_link = await get_reels_link(data_donor) #Получение первых 9 ссылок на reels

    except Exception as ex:
        print(f"ERROR | background_launch_parsing: {ex}")

async def get_reels_link(data_donor):
    try:
        option = Options()
        option.add_argument('--headless')  # Уберите комментарий для безголового режима
        option.add_argument('-profile')
        option.add_argument(f'{Profile_instagram}')

        service = Service(Geckodriver)
        driver = webdriver.Firefox(service=service, options=option)

        try:
            extracted_links = [link['Авторы'] for link in data_donor]

            for link in extracted_links:
                driver.get(f"{link}reels/")
                await asyncio.sleep(5)

                try:
                    # Поиск всех элементов reel
                    reel_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")

                    unpinned_links = []  # Список для хранения ссылок на незакрепленные посты

                    # Проходим по всем реелс и ищем незакрепленные посты
                    for reel in reel_elements:
                        try:
                            parent = reel.find_element(By.XPATH, "./ancestor::div[1]")
                            is_pinned = len(parent.find_elements(By.XPATH, ".//*[text()='Значок прикрепленной публикации']")) > 0
                            reel_link = reel.get_attribute("href")  # Ссылка на публикацию

                            # Если пост не закреплен, добавляем его в список
                            if not is_pinned:
                                unpinned_links.append(reel_link)

                            # Если собрано уже 9 ссылок, выходим из цикла
                            if len(unpinned_links) == 9:
                                break
                        except Exception as ex:
                            print(f"Ошибка при проверке на закрепление: {ex}")

                    await get_reels_metadata(unpinned_links)

                except Exception as ex:
                    print(f"ERROR | Ошибка обработки ссылок: {ex}")

        except Exception as ex:
            print(f"ERROR | selenium_get_reels_link: {ex}")

        finally:
            driver.quit()

    except Exception as ex:
        print(f"ERROR | selenium_parsing_reels: {ex}")

#Получаем metadata о 9 reels
async def get_reels_metadata(unpinned_links):
    try:
        loader = instaloader.Instaloader()
        loader.load_session_from_file(filename=Cookies, username=instagram_login)  # Загружаем сессию из файла

        # Мапа для хранения количества подписчиков каждого пользователя
        donor_followers_count = {}

        for link in unpinned_links:
            donor = link.split("/")[3]  # Извлекаем имя пользователя
            shortcode = link.split("/")[-2]  # Извлекаем shortcode рилса

            try:
                # Проверяем, есть ли уже количество подписчиков для этого пользователя в мапе
                if donor not in donor_followers_count:

                    # Загружаем профиль пользователя и получаем количество подписчиков
                    profile = instaloader.Profile.from_username(loader.context, donor)

                    followers = profile.followers

                    donor_followers_count[donor] = followers
                    await insert_add_or_update_followers(donor, followers)
                    await google_sheet_add_followers(donor, followers)

                # Загружаем пост с использованием shortcode
                post = instaloader.Post.from_shortcode(loader.context, shortcode)

                # Извлекаем необходимые данные
                post_date = post.date  # Дата рилса
                post_date_add = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Дата добавления (если она доступна)
                caption = post.caption  # Описание
                views = post.video_view_count if post.is_video else None  # Просмотры (для видео)
                likes = post.likes  # Лайки
                comments = post.comments  # Количество комментариев
                reposts = post.reposts_count if hasattr(post, 'reposts_count') else 0  # Репосты (если атрибут доступен)

                # Получаем количество подписчиков из мапы
                followers = donor_followers_count[donor]

                # Вставляем или обновляем данные о рилсе и добавляем в Google Sheet
                await insert_or_update_link(donor, link, post_date, post_date_add, caption, views, likes, comments, reposts)
                await google_sheet_add_reception(donor, link, post_date, post_date_add, caption, views, likes, comments, reposts)
                await asyncio.sleep(5)

            except Exception as ex:
                print(f"ERROR | Не удалось получить данные по рилсу {shortcode}: {ex}")

    except Exception as ex:
        print(f"ERROR | get_reels_metadata: {ex}")