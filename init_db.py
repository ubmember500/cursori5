from app import db, Category, Product

def init_db():
    # Создаем таблицы
    db.create_all()
    
    # Проверяем, есть ли уже категории
    if not Category.query.first():
        # Добавляем категории
        categories = [
            Category(name='Футболки'),
            Category(name='Джинсы'),
            Category(name='Платья'),
            Category(name='Куртки'),
            Category(name='Аксессуары')
        ]
        db.session.add_all(categories)
        db.session.commit()
        
        # Добавляем товары
        products = [
            Product(name='Классическая белая футболка', 
                   description='Удобная белая футболка для повседневной носки',
                   price=19.99, 
                   image='img/products/default-product.jpg', 
                   category_id=1),
            Product(name='Футболка с принтом', 
                   description='Смелый дизайн на премиальной хлопковой футболке',
                   price=24.99, 
                   image='img/products/default-product.jpg', 
                   category_id=1),
            Product(name='Облегающие джинсы', description='Современные облегающие джинсы с эластичной тканью',
                    price=49.99, image='img/products/default-product.jpg', category_id=2),
            Product(name='Джинсы с потертостями', description='Стильные джинсы с эффектом потертости для повседневного образа',
                    price=59.99, image='img/products/default-product.jpg', category_id=2),
            Product(name='Летнее платье с цветочным принтом', description='Легкое платье с цветочным принтом, идеально для летних дней',
                    price=39.99, image='img/products/default-product.jpg', category_id=3),
            Product(name='Вечернее коктейльное платье', description='Элегантное платье для особых случаев',
                    price=79.99, image='img/products/default-product.jpg', category_id=3),
            Product(name='Кожаная куртка', description='Классическая кожаная куртка в современном стиле',
                    price=129.99, image='img/products/default-product.jpg', category_id=4),
            Product(name='Джинсовая куртка', description='Универсальная джинсовая куртка для всех сезонов',
                    price=69.99, image='img/products/default-product.jpg', category_id=4),
            Product(name='Серебряное колье', description='Нежное серебряное колье с подвеской',
                    price=29.99, image='img/products/default-product.jpg', category_id=5),
            Product(name='Кожаный ремень', description='Качественный кожаный ремень с классической пряжкой',
                    price=34.99, image='img/products/default-product.jpg', category_id=5),
        ]
        db.session.add_all(products)
        db.session.commit()
        print("База данных успешно инициализирована!")
    else:
        print("База данных уже содержит данные!")

if __name__ == '__main__':
    init_db() 