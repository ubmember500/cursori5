from app import app, db

def init_db():
    with app.app_context():
        # Проверяем, существуют ли таблицы
        from app import User
        try:
            # Пробуем получить первого пользователя
            User.query.first()
            print("База данных уже существует и содержит таблицы!")
            return
        except:
            # Если таблиц нет, создаем их
            db.create_all()
            print("Таблицы базы данных созданы!")
        
        # Import all models
        from app import Category, Product
        
        # Check if database is empty
        if not Category.query.first():
            # Create categories
            categories = [
                Category(name='Футболки'),
                Category(name='Джинсы'),
                Category(name='Платья'),
                Category(name='Куртки'),
                Category(name='Аксессуары')
            ]
            db.session.add_all(categories)
            db.session.commit()

            # Create products
            products = [
                Product(name='Классическая белая футболка', 
                       description='Удобная белая футболка для повседневной носки',
                       price=19.99, 
                       image='img/products/tshirt1.jpg', 
                       category_id=1),
                Product(name='Футболка с принтом', 
                       description='Смелый дизайн на премиальной хлопковой футболке',
                       price=24.99, 
                       image='img/products/tshirt2.jpg', 
                       category_id=1),
                Product(name='Облегающие джинсы', 
                       description='Современные облегающие джинсы с эластичной тканью',
                       price=49.99, 
                       image='img/products/jeans1.jpg', 
                       category_id=2),
                Product(name='Джинсы с потертостями', 
                       description='Стильные джинсы с эффектом потертости',
                       price=59.99, 
                       image='img/products/jeans2.jpg', 
                       category_id=2),
                Product(name='Летнее платье', 
                       description='Легкое платье с цветочным принтом',
                       price=39.99, 
                       image='img/products/dress1.jpg', 
                       category_id=3),
                Product(name='Вечернее платье', 
                       description='Элегантное платье для особых случаев',
                       price=79.99, 
                       image='img/products/dress2.jpg', 
                       category_id=3),
                Product(name='Кожаная куртка', 
                       description='Классическая кожаная куртка',
                       price=129.99, 
                       image='img/products/jacket1.jpg', 
                       category_id=4),
                Product(name='Джинсовая куртка', 
                       description='Универсальная джинсовая куртка',
                       price=69.99, 
                       image='img/products/jacket2.jpg', 
                       category_id=4),
                Product(name='Серебряное колье', 
                       description='Нежное серебряное колье с подвеской',
                       price=29.99, 
                       image='img/products/accessory1.jpg', 
                       category_id=5),
                Product(name='Кожаный ремень', 
                       description='Качественный кожаный ремень',
                       price=34.99, 
                       image='img/products/accessory2.jpg', 
                       category_id=5)
            ]
            db.session.add_all(products)
            db.session.commit()
            print("База данных успешно инициализирована с тестовыми данными!")
        else:
            print("База данных уже содержит данные!")

if __name__ == '__main__':
    init_db() 