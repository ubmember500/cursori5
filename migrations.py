from app import db, app, Order, OrderItem
import os

def migrate():
    with app.app_context():
        # Проверяем существующие таблицы
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Существующие таблицы: {existing_tables}")
        
        # Проверяем, существует ли таблица orders
        if 'orders' not in existing_tables:
            print("Таблица 'orders' не существует, создаем...")
        else:
            print("Таблица 'orders' уже существует")
            
        # Проверяем, существует ли таблица order_items
        if 'order_items' not in existing_tables:
            print("Таблица 'order_items' не существует, создаем...")
        else:
            print("Таблица 'order_items' уже существует")
        
        # Создаем таблицы для заказов
        db.create_all()
        
        # Проверяем, что таблицы созданы
        inspector = inspect(db.engine)
        updated_tables = inspector.get_table_names()
        print(f"Таблицы после миграции: {updated_tables}")
        
        # Проверяем структуру таблиц
        if 'orders' in updated_tables:
            columns = inspector.get_columns('orders')
            print(f"Структура таблицы 'orders': {[col['name'] for col in columns]}")
        
        if 'order_items' in updated_tables:
            columns = inspector.get_columns('order_items')
            print(f"Структура таблицы 'order_items': {[col['name'] for col in columns]}")
        
        print("Миграция успешно выполнена")

if __name__ == '__main__':
    migrate() 