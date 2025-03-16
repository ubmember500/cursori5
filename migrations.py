from app import db, app

def migrate():
    with app.app_context():
        # Создаем таблицы для заказов
        db.create_all()
        print("Миграция успешно выполнена")

if __name__ == '__main__':
    migrate() 