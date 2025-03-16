from app import db, app, Order, OrderItem
import os
from sqlalchemy import inspect, text

def migrate():
    with app.app_context():
        # Проверяем существующие таблицы
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Существующие таблицы: {tables}")
        
        # Проверяем, существует ли таблица order
        if 'order' in tables:
            print("Таблица 'order' существует")
            
            # Проверяем, есть ли колонка messenger_contact
            columns = inspector.get_columns('order')
            column_names = [col['name'] for col in columns]
            
            if 'messenger_contact' not in column_names:
                print("Колонка 'messenger_contact' не существует, добавляем...")
                
                # Добавляем колонку messenger_contact
                try:
                    db.engine.execute(text("ALTER TABLE 'order' ADD COLUMN messenger_contact VARCHAR(100)"))
                    print("Колонка 'messenger_contact' успешно добавлена")
                except Exception as e:
                    print(f"Ошибка при добавлении колонки: {e}")
            else:
                print("Колонка 'messenger_contact' уже существует")
        else:
            print("Таблица 'order' не существует, создаем таблицы...")
            db.create_all()
            print("Таблицы созданы")
        
        # Проверяем структуру таблиц после миграции
        inspector = inspect(db.engine)
        if 'order' in inspector.get_table_names():
            columns = inspector.get_columns('order')
            print(f"Структура таблицы 'order' после миграции: {[col['name'] for col in columns]}")
        
        print("Миграция успешно выполнена")

if __name__ == '__main__':
    migrate() 