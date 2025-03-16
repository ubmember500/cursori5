from app import db, app, Order, OrderItem, User
import os
from sqlalchemy import inspect

def check_db():
    with app.app_context():
        # Проверяем существующие таблицы
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Таблицы в базе данных:", tables)
        
        # Проверяем пользователей
        users = User.query.all()
        print(f"Количество пользователей: {len(users)}")
        for user in users:
            print(f"Пользователь: {user.id}, {user.username}, {user.email}")
        
        # Проверяем заказы
        try:
            orders = Order.query.all()
            print(f"Количество заказов: {len(orders)}")
            for order in orders:
                print(f"Заказ: {order.id}, пользователь: {order.user_id}, сумма: {order.total_amount}")
                for item in order.items:
                    print(f"  Товар: {item.product_id}, количество: {item.quantity}, цена: {item.price}")
        except Exception as e:
            print(f"Ошибка при получении заказов: {e}")
        
        # Проверяем таблицу order (а не orders)
        if 'order' in tables:
            columns = inspector.get_columns('order')
            column_names = [col['name'] for col in columns]
            print("Колонки в таблице order:", column_names)
            
            if 'messenger_contact' not in column_names:
                print("ОШИБКА: Колонка 'messenger_contact' отсутствует в таблице order!")
            else:
                print("Колонка 'messenger_contact' присутствует в таблице order.")
        else:
            print("ОШИБКА: Таблица 'order' не найдена в базе данных!")
        
        # Проверяем таблицу order_item (а не order_items)
        if 'order_item' in tables:
            columns = inspector.get_columns('order_item')
            column_names = [col['name'] for col in columns]
            print("Колонки в таблице order_item:", column_names)
        else:
            print("ОШИБКА: Таблица 'order_item' не найдена в базе данных!")

if __name__ == '__main__':
    check_db() 