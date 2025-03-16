from app import db, app, Order, OrderItem
import os

def migrate():
    with app.app_context():
        # Проверяем существующие таблицы
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Существующие таблицы: {existing_tables}")
        
        # Проверяем, существует ли таблица order
        if 'order' not in existing_tables:
            print("Таблица 'order' не существует, создаем...")
        else:
            print("Таблица 'order' уже существует")
            
        # Проверяем, существует ли таблица order_item
        if 'order_item' not in existing_tables:
            print("Таблица 'order_item' не существует, создаем...")
        else:
            print("Таблица 'order_item' уже существует")
        
        # Создаем таблицы для заказов
        db.create_all()
        
        # Проверяем, что таблицы созданы
        inspector = inspect(db.engine)
        updated_tables = inspector.get_table_names()
        print(f"Таблицы после миграции: {updated_tables}")
        
        print("Миграция успешно выполнена")

if __name__ == '__main__':
    migrate() 