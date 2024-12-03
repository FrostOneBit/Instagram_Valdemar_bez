import sqlite3

from psycopg2 import connect

from Config import (
    database
)

async def connect_to_database():
    try:
        connect = sqlite3.connect(database)
        cursor = connect.cursor()
        return connect, cursor
    except Exception as ex:
        print(f"ERROR | connect_to_database: {ex}")
    finally:
        cursor.close()
        connect.close()

async def create_table_for_database():
    try:
        # Подключение к базе данных
        connect, cursor = await connect_to_database()

        # Создание таблицы
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Links (
                Id BIGINT AUTO_INCREMENT PRIMARY KEY,
                _link TEXT,
                _data_add TEXT,
                _caption TEXT,
                _views TEXT,
                _likes TEXT,
                _count_comments TEXT,
                _reposts TEXT
            )
            """
        )

        # Применение изменений
        connect.commit()

    except Exception as ex:
        print(f"ERROR | create_table_for_database: {ex}")

    finally:
        # Закрытие соединения
        connect.close()