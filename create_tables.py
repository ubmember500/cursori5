from app import app, db, Order, OrderItem

# Создаем контекст приложения
with app.app_context():
    # Создаем таблицы
    db.create_all()
    
    # Проверяем, что таблицы созданы
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    tables = inspector.get_table_names()
    print("Существующие таблицы в базе данных:")
    for table in tables:
        print(f"- {table}")
    
    # Проверяем, созданы ли таблицы orders и order_items
    if 'orders' in tables and 'order_items' in tables:
        print("\nТаблицы orders и order_items успешно созданы!")
    else:
        missing = []
        if 'orders' not in tables:
            missing.append('orders')
        if 'order_items' not in tables:
            missing.append('order_items')
        print(f"\nВНИМАНИЕ: Следующие таблицы не были созданы: {', '.join(missing)}")
        print("Проверьте права доступа к базе данных и структуру моделей.")

print("Скрипт создания таблиц завершен.") 