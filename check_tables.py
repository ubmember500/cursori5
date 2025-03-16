from app import app, db

with app.app_context():
    # Получаем список всех таблиц
    tables = db.engine.table_names()
    print("Существующие таблицы в базе данных:")
    for table in tables:
        print(f"- {table}")

    # Проверяем структуру таблицы User
    if 'user' in tables:
        result = db.engine.execute("PRAGMA table_info('user')")
        print("\nСтруктура таблицы User:")
        for row in result:
            print(f"- {row['name']} ({row['type']})") 