import asyncio
from Parser import launch_parsing
from Database import create_table_for_database


async def main():
    while True:
        print("\nВыберите действие:")
        print("1. Начать парсить")
        print("2. Выход")

        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            print("Создаём таблицы в базе данных...")
            await create_table_for_database()
            print("Таблицы успешно созданы. Запускаем парсинг...")
            await launch_parsing()
            print("Парсинг завершён.")
        elif choice == "2":
            print("Выход из программы.")
            break
        else:
            print("Некорректный ввод. Попробуйте снова.")


# Запуск основного цикла
if __name__ == "__main__":
    asyncio.run(main())
