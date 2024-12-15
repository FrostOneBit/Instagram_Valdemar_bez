import asyncio
import sqlite3

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

async def create_table_for_database():
    try:
        # Подключение к базе данных
        connect, cursor = await connect_to_database()

        # Создание таблицы
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Links (
                Id INTEGET PRIMARY KEY,
                _author TEXT,
                _link TEXT,
                _date_reels TEXT,
                _data_add TEXT,
                _caption TEXT,
                _views TEXT,
                _likes TEXT,
                _count_comments TEXT,
                _reposts TEXT
            )
            """
        )

    except Exception as ex:
        print(f"ERROR | create_table_for_database: {ex}")

    finally:
        connect.commit()


asyncio.run(create_table_for_database())