from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Создаем приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cursor_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'cursor_shop_secret_key'

# Создаем объект базы данных
db = SQLAlchemy(app)

# Определяем модели
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=10)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

# Создаем базу данных и таблицы
with app.app_context():
    print("Создаем базу данных...")
    db.create_all()
    print("База данных создана успешно!")
    
    # Добавляем тестовые данные
    print("Добавляем тестовые данные...")
    
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
    print("Категории добавлены!")
    
    # Добавляем продукты
    products = [
        # Футболки
        Product(name='Классическая белая футболка', 
                description='Удобная белая футболка для повседневной носки',
                price=19.99, 
                image='tshirt1.jpg', 
                stock=10,
                category_id=1),
        Product(name='Футболка с принтом', 
                description='Смелый дизайн на премиальной хлопковой футболке',
                price=24.99, 
                image='tshirt2.jpg', 
                stock=10,
                category_id=1),
        Product(name='Футболка с логотипом', 
                description='Стильная футболка с минималистичным логотипом',
                price=29.99, 
                image='tshirt3.jpg', 
                stock=15,
                category_id=1),
        Product(name='Футболка с вышивкой', 
                description='Элегантная футболка с ручной вышивкой',
                price=34.99, 
                image='tshirt4.jpg', 
                stock=8,
                category_id=1),
        
        # Джинсы
        Product(name='Облегающие джинсы', 
                description='Современные облегающие джинсы с эластичной тканью',
                price=49.99, 
                image='jeans1.jpg', 
                stock=12,
                category_id=2),
        Product(name='Джинсы с потертостями', 
                description='Стильные джинсы с эффектом потертости для повседневного образа',
                price=59.99, 
                image='jeans2.jpg', 
                stock=15,
                category_id=2),
        Product(name='Классические джинсы', 
                description='Традиционные джинсы прямого кроя',
                price=45.99, 
                image='jeans3.jpg', 
                stock=20,
                category_id=2),
        Product(name='Джинсы с высокой посадкой', 
                description='Модные джинсы с высокой посадкой и зауженным кроем',
                price=54.99, 
                image='jeans4.jpg', 
                stock=10,
                category_id=2),
        
        # Платья
        Product(name='Летнее платье с цветочным принтом', 
                description='Легкое платье с цветочным принтом, идеально для летних дней',
                price=39.99, 
                image='dress1.jpg', 
                stock=8,
                category_id=3),
        Product(name='Вечернее коктейльное платье', 
                description='Элегантное платье для особых случаев',
                price=79.99, 
                image='dress2.jpg', 
                stock=5,
                category_id=3),
        Product(name='Платье-футляр', 
                description='Классическое платье-футляр для делового стиля',
                price=69.99, 
                image='dress3.jpg', 
                stock=10,
                category_id=3),
        Product(name='Повседневное платье', 
                description='Удобное платье для повседневной носки',
                price=45.99, 
                image='dress4.jpg', 
                stock=15,
                category_id=3),
        
        # Куртки
        Product(name='Кожаная куртка', 
                description='Классическая кожаная куртка в современном стиле',
                price=129.99, 
                image='jacket1.jpg', 
                stock=6,
                category_id=4),
        Product(name='Джинсовая куртка', 
                description='Универсальная джинсовая куртка для всех сезонов',
                price=69.99, 
                image='jacket2.jpg', 
                stock=12,
                category_id=4),
        Product(name='Ветровка', 
                description='Легкая ветровка для прохладной погоды',
                price=49.99, 
                image='jacket3.jpg', 
                stock=15,
                category_id=4),
        Product(name='Куртка-бомбер', 
                description='Стильная куртка-бомбер с современным дизайном',
                price=89.99, 
                image='jacket4.jpg', 
                stock=8,
                category_id=4),
        
        # Аксессуары
        Product(name='Серебряное колье', 
                description='Нежное серебряное колье с подвеской',
                price=29.99, 
                image='accessory1.jpg', 
                stock=20,
                category_id=5),
        Product(name='Кожаный ремень', 
                description='Качественный кожаный ремень с классической пряжкой',
                price=34.99, 
                image='accessory2.jpg', 
                stock=25,
                category_id=5),
        Product(name='Шелковый шарф', 
                description='Элегантный шелковый шарф с цветочным принтом',
                price=39.99, 
                image='accessory3.jpg', 
                stock=15,
                category_id=5),
        Product(name='Кожаная сумка', 
                description='Стильная кожаная сумка с отделениями',
                price=89.99, 
                image='accessory4.jpg', 
                stock=10,
                category_id=5)
    ]
    db.session.add_all(products)
    db.session.commit()
    print("Продукты добавлены!")
    
    print("Все готово! База данных создана и заполнена тестовыми данными.") 