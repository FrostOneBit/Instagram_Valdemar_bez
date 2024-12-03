import psycopg2

from Config import (
    database,
    user_db,
    port_db,
    password_db,
    localhost_db
)

async def connect_to_database():
    try:
        connect = psycopg2.connect(dbname=database, user=user_db, password=password_db, host=localhost_db, port=port_db)
        cursor = connect.cursor()
        return connect, cursor
    except Exception as ex:
        print(f"ERROR | connect_to_database: {ex}")
    finally:
        cursor.close()
        connect.close()