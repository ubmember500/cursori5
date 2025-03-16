from app import app, db, User, Order, OrderItem, Product
from sqlalchemy import inspect, text

def check_db_structure():
    with app.app_context():
        # Проверяем существующие таблицы
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Таблицы в базе данных:", tables)
        
        # Проверяем структуру таблицы order
        if 'order' in tables:
            try:
                # Используем PRAGMA для получения информации о таблице
                result = db.session.execute(text("PRAGMA table_info('order')"))
                print("\nСтруктура таблицы order:")
                for row in result:
                    print(row)
                
                # Проверяем внешние ключи
                foreign_keys = inspector.get_foreign_keys('order')
                print("\nВнешние ключи таблицы order:", foreign_keys)
                
                # Проверяем данные в таблице
                orders = db.session.execute(text("SELECT * FROM 'order' LIMIT 5")).fetchall()
                print("\nПримеры данных в таблице order:")
                for order in orders:
                    print(order)
            except Exception as e:
                print(f"Ошибка при проверке таблицы order: {e}")
        else:
            print("Таблица order не найдена в базе данных!")
        
        # Проверяем структуру таблицы order_item
        if 'order_item' in tables:
            try:
                # Используем PRAGMA для получения информации о таблице
                result = db.session.execute(text("PRAGMA table_info('order_item')"))
                print("\nСтруктура таблицы order_item:")
                for row in result:
                    print(row)
                
                # Проверяем внешние ключи
                foreign_keys = inspector.get_foreign_keys('order_item')
                print("\nВнешние ключи таблицы order_item:", foreign_keys)
                
                # Проверяем данные в таблице
                items = db.session.execute(text("SELECT * FROM order_item LIMIT 5")).fetchall()
                print("\nПримеры данных в таблице order_item:")
                for item in items:
                    print(item)
            except Exception as e:
                print(f"Ошибка при проверке таблицы order_item: {e}")
        else:
            print("Таблица order_item не найдена в базе данных!")
        
        # Проверяем модели SQLAlchemy
        print("\nПроверка моделей SQLAlchemy:")
        try:
            # Проверяем модель Order
            order_attrs = [attr for attr in dir(Order) if not attr.startswith('_')]
            print(f"Атрибуты модели Order: {order_attrs}")
            
            # Проверяем модель OrderItem
            order_item_attrs = [attr for attr in dir(OrderItem) if not attr.startswith('_')]
            print(f"Атрибуты модели OrderItem: {order_item_attrs}")
        except Exception as e:
            print(f"Ошибка при проверке моделей: {e}")

if __name__ == "__main__":
    check_db_structure() 