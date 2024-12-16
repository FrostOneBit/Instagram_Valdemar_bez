import asyncio
import time
from datetime import datetime, timedelta
from tkinter.ttk import Label

from Parser import launch_parsing
from Database import create_table_for_database

def start_check_time():
    try:
        while True:
            check_time_and_run()
            print("Спим минуту")
            time.sleep(1)
    except Exception as ex:
        print(f"ERROR | start_check_time: {ex}")

async def task():
    # Здесь вставьте вашу функцию
    print("Запуск функции check_and_parse")
    await launch_parsing()

def run_task():
    asyncio.run(task())

def check_time_and_run():
    try:
        current_time = datetime.now()
        scheduled_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        # Допустимое отклонение времени (в минутах)
        tolerance_minutes = 5
        start_window = scheduled_time - timedelta(minutes=tolerance_minutes)
        end_window = scheduled_time + timedelta(minutes=tolerance_minutes)

        if start_window <= current_time <= end_window:
            print(f"Время {current_time.strftime('%H:%M')} попадает в интервал запуска. Задача будет запущена.")
            run_task()
        else:
            print(f"Текущее время {current_time.strftime('%H:%M')}. Время запуска еще не наступило.")

    except Exception as ex:
        print(f"ERROR | check_time_and_run: {ex}")

asyncio.run(create_table_for_database())
start_check_time()