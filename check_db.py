from app import db, app, Order, OrderItem, User
import os

def check_db():
    with app.app_context():
        # Проверяем существующие таблицы
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Существующие таблицы: {existing_tables}")
        
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
        
        # Проверяем структуру таблиц
        if 'orders' in existing_tables:
            columns = inspector.get_columns('orders')
            print(f"Структура таблицы 'orders': {[col['name'] for col in columns]}")
        
        if 'order_items' in existing_tables:
            columns = inspector.get_columns('order_items')
            print(f"Структура таблицы 'order_items': {[col['name'] for col in columns]}")

if __name__ == '__main__':
    check_db() 