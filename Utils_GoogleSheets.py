import gspread
from oauth2client.service_account import ServiceAccountCredentials

from Config import (
    Google_service_file,
    Google_table,
    Google_donor,
    Google_reception
)

from datetime import datetime, timedelta

#Получаем список аккаунтов (Доноров)
async def google_sheet_read_donor():
    try:
        # Задать путь к JSON с учётными данными
        credentials_file = Google_service_file

        # Определить область действия для авторизации
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)

        # Авторизация
        client = gspread.authorize(creds)

        # Указать ID таблицы (можно взять из URL Google Sheets)
        spreadsheet_id = Google_table

        # Открытие таблицы
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Поиск листа по gid
        donor_worksheet = None
        for worksheet in spreadsheet.worksheets():
            if worksheet.id == Google_donor:  # `worksheet.id` возвращает gid листа
                donor_worksheet = worksheet
                break

        if donor_worksheet is None:
            raise ValueError(f"ERROR | Лист с gid={Google_donor} не найден.")

        # Чтение всех данных из листа
        data = donor_worksheet.get_all_records()  # Считает данные в виде списка словарей
        return True, data

    except Exception as ex:
        print(f"ERROR | google_sheet_read_donor: {ex}")
        return False, None

async def google_sheet_add_reception(donor, link, post_date, post_date_add, caption, views, likes, comments, reposts):
    try:
        # Задать путь к JSON с учётными данными
        credentials_file = Google_service_file

        # Определить область действия для авторизации
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)

        # Авторизация
        client = gspread.authorize(creds)

        # Указать ID таблицы (можно взять из URL Google Sheets)
        spreadsheet_id = Google_table

        # Открытие таблицы
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Поиск листа по gid
        donor_worksheet = None
        for worksheet in spreadsheet.worksheets():
            if worksheet.id == Google_reception:  # `worksheet.id` возвращает gid листа
                donor_worksheet = worksheet
                break

        if not donor_worksheet:
            print(f"Лист с gid {Google_reception} не найден.")
            return

        # Получаем все данные из листа
        data = donor_worksheet.get_all_records()

        current_date = datetime.now()

        # Проверяем, существует ли ссылка в таблице
        existing_link_row = None
        for row in data:
            if row['Ссылка'] == link:
                existing_link_row = row
                break

        # Проверяем и конвертируем даты, если они строки
        if isinstance(post_date, str):
            post_date = datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(post_date_add, str):
            post_date_add = datetime.strptime(post_date_add, "%Y-%m-%d %H:%M:%S")

        # Преобразуем даты в строковый формат
        post_date_str = post_date.strftime("%Y-%m-%d %H:%M:%S")
        post_date_add_str = post_date_add.strftime("%Y-%m-%d %H:%M:%S")

        if existing_link_row:
            # Если ссылка уже существует, проверяем дату добавления
            try:
                date_added = datetime.strptime(existing_link_row['Дата обновления'], "%Y-%m-%d %H:%M:%S")  # _data_add в формате "YYYY-MM-DD HH:MM:SS"

                if current_date - date_added > timedelta(days=10):
                    # Если прошло более 10 дней, удаляем запись
                    row_index = data.index(existing_link_row) + 2  # Строки в Google Sheets начинаются с 1, а не с 0
                    donor_worksheet.delete_rows(row_index)
                    print(f"Запись для {link} удалена, так как она старше 10 дней.")
                else:
                    # Если прошло менее 10 дней, обновляем информацию
                    row_index = data.index(existing_link_row) + 2  # Строки в Google Sheets начинаются с 1, а не с 0
                    donor_worksheet.update_cell(row_index, 4, current_date.strftime("%Y-%m-%d %H:%M:%S"))  # Обновляем дату
                    donor_worksheet.update_cell(row_index, 6, views)  # Обновляем просмотры
                    donor_worksheet.update_cell(row_index, 7, likes)  # Обновляем лайки
                    donor_worksheet.update_cell(row_index, 8, comments)  # Обновляем комментарии
                    donor_worksheet.update_cell(row_index, 9, reposts)  # Обновляем репосты
                    print(f"Данные для {link} обновлены.")
            except ValueError:
                print(f"Ошибка при разборе даты обновления для {link}.")
        else:
            # Если ссылки нет, добавляем новую запись
            donor_worksheet.append_row([donor, link, post_date_str, post_date_add_str, caption, views, likes, comments, reposts])
            print(f"Новая запись добавлена для {link}. В Google Sheet.")

    except Exception as ex:
        print(f"ERROR | google_sheet_add_reception: {ex}")

async def google_sheet_add_followers(donor, followers):
    try:
        # Задать путь к JSON с учётными данными
        credentials_file = Google_service_file

        # Определить область действия для авторизации
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)

        # Авторизация
        client = gspread.authorize(creds)

        # Указать ID таблицы (можно взять из URL Google Sheets)
        spreadsheet_id = Google_table

        # Открытие таблицы
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Поиск листа с авторами
        author_worksheet = None
        for worksheet in spreadsheet.worksheets():
            if worksheet.id == Google_donor:  # Здесь должен быть `gid` листа с авторами
                author_worksheet = worksheet
                break

        if not author_worksheet:
            print(f"Лист с gid {Google_donor} не найден.")
            return

        # Получаем все данные из листа
        data = author_worksheet.get_all_records()

        # Поиск строки с указанным автором
        row_index = None
        for i, row in enumerate(data, start=2):  # Строки в Google Sheets начинаются с 1, +1 для заголовков
            if row['Авторы'] == f"https://www.instagram.com/{donor}/":
                row_index = i
                break

        if row_index:
            # Обновляем количество подписчиков
            author_worksheet.update_cell(row_index, 2, followers)  # Колонка 2 — "Кол-во подписчиков"
            print(f"Количество подписчиков для {donor} обновлено: {followers}.")
        else:
            # Если автор не найден, добавляем новую запись
            author_worksheet.append_row([f"https://www.instagram.com/{donor}/", followers])
            print(f"Добавлен новый автор: {donor} с количеством подписчиков {followers}.")

    except Exception as ex:
        print(f"ERROR | google_sheet_add_followers: {ex}")
