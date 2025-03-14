from flask_migrate import Migrate
from app import app, db
from sqlalchemy.exc import SQLAlchemyError

def upgrade():
    try:
        print("\n=== Начало миграции базы данных ===")
        
        with app.app_context():
            from app import Order
            
            # Проверяем существование таблицы order
            inspector = db.inspect(db.engine)
            if 'order' not in inspector.get_table_names():
                print("Ошибка: Таблица 'order' не найдена")
                return
            
            # Проверяем существование колонки user_id
            columns = [col['name'] for col in inspector.get_columns('order')]
            if 'user_id' not in columns:
                print("Ошибка: Колонка 'user_id' не найдена")
                return
            
            # Удаляем заказы без привязки к пользователю
            orders_to_delete = Order.query.filter_by(user_id=None).all()
            if orders_to_delete:
                print(f"Найдено {len(orders_to_delete)} заказов без привязки к пользователю")
                for order in orders_to_delete:
                    print(f"Удаление заказа #{order.id}")
                Order.query.filter_by(user_id=None).delete()
                db.session.commit()
                print("Заказы без привязки к пользователю успешно удалены")
            
            # Делаем поле user_id обязательным
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE "order" ALTER COLUMN user_id SET NOT NULL;')
                conn.commit()
                print("Поле user_id успешно сделано обязательным")
        
        print("=== Миграция успешно завершена ===\n")
        
    except SQLAlchemyError as e:
        print(f"Ошибка SQLAlchemy при миграции: {str(e)}")
        raise
    except Exception as e:
        print(f"Неожиданная ошибка при миграции: {str(e)}")
        raise

def downgrade():
    try:
        print("\n=== Начало отката миграции ===")
        
        with app.app_context():
            # Проверяем существование таблицы order
            inspector = db.inspect(db.engine)
            if 'order' not in inspector.get_table_names():
                print("Ошибка: Таблица 'order' не найдена")
                return
            
            # Проверяем существование колонки user_id
            columns = [col['name'] for col in inspector.get_columns('order')]
            if 'user_id' not in columns:
                print("Ошибка: Колонка 'user_id' не найдена")
                return
            
            # Делаем поле user_id необязательным
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE "order" ALTER COLUMN user_id DROP NOT NULL;')
                conn.commit()
                print("Поле user_id успешно сделано необязательным")
        
        print("=== Откат миграции успешно завершен ===\n")
        
    except SQLAlchemyError as e:
        print(f"Ошибка SQLAlchemy при откате миграции: {str(e)}")
        raise
    except Exception as e:
        print(f"Неожиданная ошибка при откате миграции: {str(e)}")
        raise 