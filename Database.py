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
    finally:
        cursor.close()
        connect.close()