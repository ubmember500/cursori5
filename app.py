import base64
from functools import wraps
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

# Функции шифрования
def encrypt_password(password):
    return base64.b64encode(password.encode()).decode()

def decrypt_password(encrypted_password):
    return base64.b64decode(encrypted_password.encode()).decode()

def encrypt_mail_password(password):
    return base64.b64encode(password.encode()).decode()

def decrypt_mail_password(encrypted_password):
    return base64.b64decode(encrypted_password.encode()).decode()

# Загружаем переменные окружения из .env файла
load_dotenv()

# Зашифрованный пароль (можно безопасно хранить в GitHub)
ENCRYPTED_MAIL_PASSWORD = "c254bHRycG56eXRyZnJibA=="

# Генерируем правильное значение
original_password = "snxltrpnzytrfrbl"
correct_encrypted = encrypt_mail_password(original_password)
print(f"\nПравильное зашифрованное значение: {correct_encrypted}\n")

# Используем правильное значение
ENCRYPTED_MAIL_PASSWORD = "c254bHRycG56eXRyZnJibA=="

# Расшифровываем и выводим для проверки
decrypted_password = decrypt_mail_password(ENCRYPTED_MAIL_PASSWORD)
print("\n=== Проверка пароля ===")
print(f"Зашифрованный пароль: {ENCRYPTED_MAIL_PASSWORD}")
print(f"Расшифрованный пароль: {decrypted_password}")
print("=======================\n")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Пожалуйста, войдите в систему для доступа к этой странице', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# from liqpay import LiqPay  # Temporarily commented out

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time
import random
import requests
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask_caching import Cache
from functools import lru_cache, wraps
from threading import Thread
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import bleach
import re
from sqlalchemy.exc import IntegrityError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Настройка путей
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR, mode=0o777)

# Конфигурация социальных сетей
SOCIAL_MEDIA = {
    'instagram': 'https://instagram.com/greleolxpw',
    'telegram': 'https://t.me/Cursor_shop'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(INSTANCE_DIR, "shop.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SOCIAL_MEDIA'] = SOCIAL_MEDIA

# Отключаем кэширование шаблонов
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Настройка безопасной сессии
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Конфигурация Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))  # Используем порт 587 для TLS
app.config['MAIL_USE_SSL'] = False  # Отключаем SSL
app.config['MAIL_USE_TLS'] = True   # Включаем TLS
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'defensivelox@gmail.com')
app.config['MAIL_PASSWORD'] = decrypt_mail_password(ENCRYPTED_MAIL_PASSWORD)
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'defensivelox@gmail.com')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'defensivelox@gmail.com')

print("\n=== Настройки SMTP ===")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print(f"ADMIN_EMAIL: {app.config['ADMIN_EMAIL']}")
print("================================================")

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Явное подключение к почтовому серверу
with app.app_context():
    try:
        mail.connect()
        print("Успешное подключение к почтовому серверу")
    except Exception as e:
        print(f"Ошибка подключения к почтовому серверу: {e}")

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Middleware для защиты от XSS
def xss_protection_middleware():
    def sanitize_input(text):
        if isinstance(text, str):
            # Очистка HTML-тегов
            text = bleach.clean(text, tags=[], attributes={}, strip=True)
            # Экранирование специальных символов
            text = bleach.linkify(text)
            return text
        return text

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            g.user = current_user
        else:
            g.user = None
        
        # Инициализируем корзину
        if 'cart' not in session:
            session['cart'] = []
        # Защита данных формы
        if request.form:
            request.form = {k: sanitize_input(v) for k, v in request.form.items()}
        # Защита параметров URL
        if request.args:
            request.args = {k: sanitize_input(v) for k, v in request.args.items()}
        # Защита JSON данных
        if request.is_json:
            json_data = request.get_json()
            if isinstance(json_data, dict):
                request._cached_json = {k: sanitize_input(v) for k, v in json_data.items()}

    @app.after_request
    def after_request(response):
        # Добавляем дополнительные заголовки безопасности
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Добавляем заголовки кэширования только для не-AJAX запросов
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response

# Активируем middleware
xss_protection_middleware()

# LiqPay configuration
# LIQPAY_PUBLIC_KEY = os.getenv('LIQPAY_PUBLIC_KEY')
# LIQPAY_PRIVATE_KEY = os.getenv('LIQPAY_PRIVATE_KEY')

# Cache configuration
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
cache.init_app(app)

# Upload folder configuration
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=10)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
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
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': self.is_active
        }


class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)


class NewsletterSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, processing, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    items = db.Column(db.JSON)  # Хранит список товаров в формате JSON
    customer_info = db.Column(db.JSON)  # Хранит информацию о покупателе
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', backref='orders')


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True)
    data = db.Column(db.Text)
    expiry = db.Column(db.DateTime)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(20))
    color = db.Column(db.String(50))
    order = db.relationship('Order', backref='order_items')
    product = db.relationship('Product')


# Create database tables
def init_db():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        
        # Только после создания таблиц пытаемся очистить сессии
        cleanup_old_sessions()
        
        # Add sample data if the database is empty
        if not Category.query.first():
            categories = [
                Category(name='Футболки'),
                Category(name='Джинсы'),
                Category(name='Платья'),
                Category(name='Куртки'),
                Category(name='Аксессуары')
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            products = [
                Product(name='Классическая белая футболка', description='Удобная белая футболка для повседневной носки',
                        price=19.99, image='img/products/default-product.jpg', category_id=1),
                Product(name='Футболка с принтом', description='Смелый дизайн на премиальной хлопковой футболке',
                        price=24.99, image='img/products/default-product.jpg', category_id=1),
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
        print("Database initialized successfully!")


@app.context_processor
def inject_categories():
    try:
        categories = Category.query.all()
        return dict(categories=categories)
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return dict(categories=[])

@app.context_processor
def inject_social_media():
    print("Social media URLs:", SOCIAL_MEDIA)  # Отладочный вывод
    return dict(social_media=SOCIAL_MEDIA)

def get_random_product_image(category_id):
    try:
        category_map = {
            1: 'tshirt',
            2: 'jeans',
            3: 'dress',
            4: 'jacket',
            5: 'accessory'
        }
        
        if category_id in category_map:
            base_name = category_map[category_id]
            image_name = f'{base_name}1.jpg'  # Используем первое изображение из каждой категории
            image_path = f'img/products/{image_name}'
            if os.path.exists(os.path.join('static', image_path)):
                return image_path
        return 'img/products/default-product.jpg'
    except Exception as e:
        print(f"Ошибка при получении изображения: {e}")
        return 'img/products/default-product.jpg'


def download_and_save_image(url, product_id):
    # В данном случае просто возвращаем путь к изображению
    return url


# Кэширование с версионированием
_cache_version = int(time.time())

def invalidate_cache():
    global _cache_version
    _cache_version = int(time.time())

@lru_cache(maxsize=32)
def get_cached_products(category_id=None, search_query=None, cache_version=None):
    # cache_version игнорируется в логике, но используется для инвалидации кэша
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    return query.all()

# Очистка старых сессий
def cleanup_old_sessions():
    try:
        sessions = Session.query.filter(
            Session.expiry < datetime.utcnow()
        ).all()
        for session in sessions:
            db.session.delete(session)
        db.session.commit()
        print("Session cleanup completed")
    except Exception as e:
        app.logger.error(f'Error cleaning up sessions: {str(e)}')
        db.session.rollback()

# Запускаем очистку сессий каждый день
with app.app_context():
    cleanup_old_sessions()
    print("Session cleanup completed")

# Обновляем кэш при изменении товаров
@app.after_request
def after_request(response):
    if request.endpoint in ['add_product', 'edit_product', 'delete_product']:
        invalidate_cache()
    return response

@app.route('/')
def home():
    featured_products = Product.query.limit(6).all()
    # Обновляем изображения для товаров
    for product in featured_products:
        product.image = get_random_product_image(product.category_id)
    return render_template('home.html', products=featured_products)


@app.route('/products')
def products():
    try:
        print("\n=== Начало обработки запроса /products ===")
        print(f"Все параметры запроса: {request.args}")
        print(f"Заголовки запроса: {dict(request.headers)}")
        
        # Получаем параметры фильтрации
        category = request.args.get('category')
        search_query = request.args.get('q')
        sort = request.args.get('sort', 'default')
        
        print(f"Параметр категории: {category}, тип: {type(category)}")
        print(f"Параметр поиска: {search_query}")
        print(f"Параметр сортировки: {sort}")
        
        # Получаем и валидируем параметры цены
        try:
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            
            print(f"Исходные параметры цены: min_price={min_price}, max_price={max_price}")
            
            # Преобразуем и валидируем минимальную цену
            if min_price is None or min_price == '':
                min_price = 0
            else:
                try:
                    min_price = float(min_price)
                except (ValueError, TypeError):
                    min_price = 0
                min_price = max(0, min(min_price, 20000))
            
            # Преобразуем и валидируем максимальную цену
            if max_price is None or max_price == '':
                max_price = 20000
            else:
                try:
                    max_price = float(max_price)
                except (ValueError, TypeError):
                    max_price = 20000
                max_price = max(min_price, min(max_price, 20000))
            
            print(f"Скорректированные параметры цены: min_price={min_price}, max_price={max_price}")
            
        except Exception as e:
            print(f"Ошибка при обработке параметров цены: {e}")
            min_price, max_price = 0, 20000
        
        # Базовый запрос
        query = Product.query
        print(f"Базовый SQL запрос: {query}")
        
        # Фильтр по категории
        if category:
            try:
                category_id = int(category)
                query = query.filter(Product.category_id == category_id)
                print(f"Применен фильтр по категории {category_id}")
                print(f"SQL запрос после фильтрации по категории: {query}")
            except (ValueError, TypeError) as e:
                print(f"Ошибка при обработке категории: {e}")
        
        # Фильтр по поиску
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
            print(f"Применен фильтр по поиску: {search_query}")
        
        # Фильтр по цене
        query = query.filter(Product.price >= min_price)
        query = query.filter(Product.price <= max_price)
        print(f"Применена фильтры по цене: {min_price} - {max_price}")
        
        # Сортировка
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'name_asc':
            query = query.order_by(Product.name.asc())
        elif sort == 'name_desc':
            query = query.order_by(Product.name.desc())
        print(f"Применена сортировка: {sort}")
        
        # Получаем все товары
        products = query.all()
        print(f"Найдено товаров: {len(products)}")
        print("Список найденных товаров:")
        for product in products:
            print(f"- {product.name} (категория: {product.category_id}, цена: {product.price})")
        
        # Получаем все категории для фильтров
        all_categories = Category.query.all()
        print(f"Всего категорий: {len(all_categories)}")
        print("Список категорий:")
        for category in all_categories:
            print(f"- {category.name} (id: {category.id})")
        
        # Обновляем изображения для товаров
        for product in products:
            product.image = get_random_product_image(product.category_id)
        
        print("=== Завершение обработки запроса /products ===\n")
        
        # Проверяем, является ли запрос AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        print(f"Это AJAX запрос: {is_ajax}")
        
        if is_ajax:
            return render_template('products_partial.html', 
                                products=products, 
                                categories=all_categories,
                                min_price=min_price,
                                max_price=max_price,
                                selected_category=category if category else None)
        
        return render_template('products.html', 
                             products=products, 
                             categories=all_categories,
                             min_price=min_price,
                             max_price=max_price,
                             selected_category=category if category else None)
        
    except Exception as e:
        print(f"Критическая ошибка в route products: {e}")
        return render_template('error.html', error="Произошла ошибка при загрузке товаров"), 500


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    # Получаем похожие товары из той же категории
    similar_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id
    ).limit(4).all()
    
    # Получаем актуальное изображение продукта
    product_image = get_random_product_image(product.category_id)
    
    # Обновляем изображения для похожих товаров
    similar_products_with_images = []
    for similar_product in similar_products:
        similar_products_with_images.append({
            'id': similar_product.id,
            'name': similar_product.name,
            'price': similar_product.price,
            'description': similar_product.description,
            'image': get_random_product_image(similar_product.category_id)
        })
    
    return render_template('product_detail.html', 
                         product=product,
                         product_image=product_image,
                         similar_products=similar_products_with_images)


@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size')
    color = request.form.get('color')
    image = request.form.get('image')

    # Получаем товар
    product = Product.query.get_or_404(product_id)
    
    # Проверяем наличие товара
    if quantity > product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Извините, данного количества товара нет в наличии'})
        flash('Извините, данного количества товара нет в наличии', 'error')
        return redirect(request.referrer or url_for('products'))

    # Убеждаемся, что у нас есть изображение и оно в правильном формате
    if not image or image == 'None':
        image = get_random_product_image(product.category_id)
    elif not image.startswith('img/products/'):
        if '/' in image:
            image = image.split('/')[-1]
        image = f'img/products/{image}'

    # Check if product is already in cart
    for item in cart:
        if item['id'] == product_id and item.get('size') == size and item.get('color') == color:
            if item['quantity'] + quantity > product.stock:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': 'Извините, данного количества товара нет в наличии'})
                flash('Извините, данного количества товара нет в наличии', 'error')
                return redirect(request.referrer or url_for('products'))
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'id': product_id,
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'size': size,
            'color': color,
            'image': image
        })
    
    session.modified = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': 'Товар успешно добавлен в корзину',
            'cart_count': len(cart)
        })
    
    flash('Товар успешно добавлен в корзину', 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart')
def cart():
    # Проверяем, нужно ли очистить корзину
    if request.args.get('clear') == 'true':
        session['cart'] = []
        session.modified = True  # Явно указываем, что сессия была изменена
        flash('Корзина очищена', 'success')
        return redirect(url_for('cart'))

    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)

    cart_items = []
    total = 0

    for item in session['cart']:
        product = Product.query.get(item['id'])
        if product:
            item_total = item['price'] * item['quantity']
            # Используем изображение из корзины, если оно есть, иначе берем из продукта
            image = item.get('image')
            if not image or image == 'None':
                image = get_random_product_image(product.category_id)
            elif not image.startswith('img/products/'):
                if '/' in image:
                    image = image.split('/')[-1]
                image = f'img/products/{image}'
            
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'total': item_total,
                'image': image,
                'size': item.get('size'),
                'color': item.get('color')
            })
            total += item_total

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))

    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if item['id'] == product_id:
                if quantity > 0:
                    item['quantity'] = quantity
                else:
                    cart.remove(item)
                session.modified = True
                break

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if item['id'] == product_id:
                cart.remove(item)
                session.modified = True
                break

    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        flash('Для оформления заказа необходимо авторизоваться', 'warning')
        return redirect(url_for('login', next=url_for('checkout')))

    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('cart'))

    cart_items = []
    total = 0

    # Проверяем наличие всех товаров перед оформлением
    for item in session['cart']:
        product = Product.query.get(item['id'])
        if not product:
            flash(f'Товар {item["name"]} больше не доступен', 'error')
            return redirect(url_for('cart'))
        
        if item['quantity'] > product.stock:
            flash(f'Товар {item["name"]} доступен только в количестве {product.stock} шт.', 'error')
            return redirect(url_for('cart'))

        item_total = item['price'] * item['quantity']
        cart_items.append({
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total,
            'image': item.get('image', '')
        })
        total += item_total

    if request.method == 'POST':
        try:
            # Создаем новый заказ в базе данных
            new_order = Order(
                user_id=current_user.id,
                total_amount=total,
                status='pending',
                items=cart_items,
                customer_info={
                    'name': current_user.first_name + ' ' + current_user.last_name,
                    'phone': current_user.phone,
                    'email': current_user.email,
                    'address': current_user.address
                },
                customer_name=current_user.first_name + ' ' + current_user.last_name,
                customer_email=current_user.email,
                customer_phone=current_user.phone,
                payment_method='Online'
            )
            
            # Уменьшаем количество товаров на складе
            for item in session['cart']:
                product = Product.query.get(item['id'])
                if product:
                    product.stock -= item['quantity']
            
            db.session.add(new_order)
            db.session.commit()
            
            # Очищаем корзину
            session.pop('cart', None)
            
            flash('Заказ успешно оформлен!', 'success')
            return redirect(url_for('my_orders'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании заказа: {str(e)}")
            flash('Произошла ошибка при оформлении заказа. Попробуйте позже.', 'error')
            return redirect(url_for('cart'))

    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/place_order', methods=['POST'])
def place_order():
    # In a real application, you would process payment and create an order in the database
    session.pop('cart', None)
    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('home'))


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Ошибка отправки email: {e}")

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Создаем текст письма
        email_body = f"""
        Новое сообщение от посетителя сайта:
        
        Имя: {name}
        Email: {email}
        Тема: {subject}
        
        Сообщение:
        {message}
        """
        
        try:
            # Отправляем email через SMTP
            if send_email_smtp(app.config['ADMIN_EMAIL'], f'Новое сообщение от {name}: {subject}', email_body):
                flash('Ваше сообщение успешно отправлено!', 'success')
            else:
                raise Exception("Не удалось отправить email через SMTP")
                
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            flash('Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.', 'danger')
        
        return redirect(url_for('contacts'))
        
    return render_template('contacts.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Проверяем, авторизован ли пользователь, и перенаправляем его на главную страницу
    if 'user_id' in session:
        flash('Вы уже зарегистрированы и вошли в систему!', 'info')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверяем, что пароли совпадают
        if password != confirm_password:
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('register'))
        
        # Проверяем, что пользователь с таким email или username еще не существует
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует!', 'danger')
            return redirect(url_for('register'))
        
        # Создаем нового пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации. Попробуйте позже.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            
            # Принудительно обновляем кэш
            cache.delete_memoized(get_cached_products)
            cache.delete('view//')
            
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            flash('Неверный логин/email или пароль!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('home'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Создаем токен для сброса пароля
            token = secrets.token_urlsafe(32)
            reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            max_attempts = 3
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    db.session.add(reset)
                    db.session.commit()
                    break
                except Exception as e:
                    attempt += 1
                    db.session.rollback()
                    if attempt == max_attempts:
                        flash('Произошла ошибка при создании токена. Пожалуйста, попробуйте позже.', 'error')
                        return redirect(url_for('forgot_password'))
                    time.sleep(1)  # Ждем секунду перед следующей попыткой
            
            try:
                # Формируем текст письма
                reset_url = url_for('reset_password', token=token, _external=True)
                email_body = f"""
                Восстановление пароля
                
                Для восстановления пароля перейдите по следующей ссылке:
                {reset_url}
                
                Ссылка действительна в течение 1 часа.
                Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.
                """
                
                # Отправляем email через SMTP
                if send_email_smtp(email, 'Восстановление пароля', email_body):
                    flash('Инструкции по восстановлению пароля отправлены на ваш email', 'success')
                    return redirect(url_for('login'))
                else:
                    raise Exception("Не удалось отправить email через SMTP")
                    
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
                flash('Произошла ошибка при отправке email. Пожалуйста, попробуйте позже.', 'error')
                return redirect(url_for('forgot_password'))
        
        flash('Email не найден', 'error')
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or reset.expires_at < datetime.utcnow():
        flash('Ссылка для восстановления пароля недействительна или истекла', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('reset_password.html')
        
        # Обновляем пароль пользователя
        user = User.query.get(reset.user_id)
        user.password_hash = generate_password_hash(password)
        
        # Удаляем использованный токен
        db.session.delete(reset)
        db.session.commit()
        
        flash('Пароль успешно изменен', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')


@app.route('/create_payment', methods=['POST'])
def create_payment():
    if not session.get('cart'):
        flash('Ваша корзина пуста', 'error')
        return redirect(url_for('cart'))
    
    # Получаем товары из корзины
    cart_items = []
    total = 0
    for item in session['cart']:
        product = Product.query.get(item['id'])
        if product:
            item_total = item['price'] * item['quantity']
            total += item_total
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'total': item_total
            })

    # Создаем уникальный ID заказа
    order_id = f"order_{int(time.time())}_{'user' if 'user_id' in session else 'guest'}"
    
    # Создаем объект LiqPay
    # liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
    
    # Формируем параметры платежа
    # params = {
    #     'action': 'pay',
    #     'amount': total,
    #     'currency': 'UAH',
    #     'description': f'Оплата заказа {order_id} в магазине Cursor Shop',
    #     'order_id': order_id,
    #     'version': '3',
    #     'sandbox': '1',  # Для тестирования. Уберите в продакшене
    #     'server_url': url_for('payment_callback', _external=True),
    #     'result_url': url_for('payment_success', _external=True)
    # }
    
    # # Генерируем форму для оплаты
    # payment_form = liqpay.cnb_form(params)
    
    return render_template('payment.html', payment_form='', total=total)

@app.route('/payment/callback', methods=['POST'])
def payment_callback():
    # liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
    data = request.form.get('data')
    signature = request.form.get('signature')
    
    # Проверяем подпись для безопасности
    # sign = liqpay.str_to_sign(LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY)
    # if sign != signature:
    #     return 'Signature verification failed', 400
    
    response = data  # Assuming the response is returned as a string
    
    # Проверяем статус платежа
    if response == 'success':
        # Здесь можно добавить логику сохранения заказа в базу данных
        # и отправки уведомления пользователю
        flash('Оплата прошла успешно!', 'success')
    else:
        flash('Произошла ошибка при оплате. Попробуйте снова.', 'error')
    
    return 'OK', 200

@app.route('/payment/success')
def payment_success():
    # Очищаем корзину после успешной оплаты
    session.pop('cart', None)
    flash('Спасибо за покупку! Мы отправим вам уведомление о статусе заказа.', 'success')
    return redirect(url_for('home'))

@app.route('/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    if not email or not is_valid_email(email):
        flash('Пожалуйста, введите корректный email адрес', 'error')
        return redirect(request.referrer or url_for('home'))
    
    # Добавление email в базу подписчиков
    try:
        subscriber = NewsletterSubscription(email=email)
        db.session.add(subscriber)
        db.session.commit()
        flash('Вы успешно подписались на рассылку!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Этот email уже подписан на рассылку', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при подписке. Попробуйте позже.', 'error')
        app.logger.error(f'Error in subscribe_newsletter: {str(e)}')
    
    return redirect(request.referrer or url_for('home'))

@app.route('/my_orders')
@login_required
def my_orders():
    try:
        print("\n=== Начало получения заказов пользователя ===")
        print(f"Текущий пользователь: {current_user.username} (ID: {current_user.id})")
        
        # Проверяем, не заблокирован ли пользователь
        if not current_user.is_active:
            print("Ошибка: Пользователь заблокирован")
            flash('Ваш аккаунт заблокирован. Пожалуйста, свяжитесь с администратором.', 'error')
            return redirect(url_for('home'))
        
        # Получаем заказы текущего пользователя по user_id
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        print(f"Найдено заказов: {len(orders)}")
        
        orders_with_items = []
        for order in orders:
            print(f"\nОбработка заказа #{order.id}:")
            print(f"- Дата создания: {order.created_at}")
            print(f"- Статус: {order.status}")
            print(f"- Сумма: {order.total_amount}")
            
            # Получаем товары из OrderItem
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            items = []
            total = 0
            
            for item in order_items:
                item_total = item.price * item.quantity
                total += item_total
                
                # Получаем изображение товара
                product = item.product
                image = get_random_product_image(product.category_id) if product else 'img/products/default-product.jpg'
                
                items.append({
                    'name': product.name if product else 'Товар недоступен',
                    'price': item.price,
                    'quantity': item.quantity,
                    'size': item.size,
                    'color': item.color,
                    'total': item_total,
                    'image': image
                })
            
            # Если нет товаров в OrderItem, пробуем использовать JSON данные
            if not items and order.items and isinstance(order.items, list):
                items = order.items
                total = sum(item.get('total', 0) for item in items)
            
            if items:
                orders_with_items.append({
                    'order': {
                        'id': order.id,
                        'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                        'status': order.status,
                        'total_amount': total,
                        'customer_info': order.customer_info
                    },
                    'items': items
                })
        
        print("=== Завершение получения заказов пользователя ===\n")
        return render_template('my_orders.html', orders=orders_with_items)
    except Exception as e:
        print(f"Ошибка при получении заказов: {str(e)}")
        flash('Произошла ошибка при загрузке заказов', 'error')
        return redirect(url_for('home'))

@app.route('/test_email')
def test_email():
    try:
        print("\n=== Тестовая отправка email ===")
        print(f"Настройки SMTP:")
        print(f"Сервер: {app.config['MAIL_SERVER']}")
        print(f"Порт: {app.config['MAIL_PORT']}")
        print(f"Пользователь: {app.config['MAIL_USERNAME']}")
        print(f"Пароль: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'Не установлен'}")
        print(f"Отправитель: {app.config['MAIL_DEFAULT_SENDER']}")
        print(f"Получатель: {app.config['ADMIN_EMAIL']}")
        
        # Отправляем тестовое письмо
        if send_email_smtp(
            app.config['ADMIN_EMAIL'],
            'Тестовое письмо от Cursor Shop',
            'Это тестовое письмо для проверки работы SMTP.'
        ):
            return jsonify({'success': True, 'message': 'Тестовое письмо успешно отправлено'})
        else:
            return jsonify({'success': False, 'message': 'Не удалось отправить тестовое письмо'})
            
    except Exception as e:
        print(f"\nОшибка при тестовой отправке: {str(e)}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

def send_email_smtp(recipient, subject, body):
    try:
        print(f"Attempting to send email to: {recipient}")
        print(f"Subject: {subject}")
        print(f"SMTP Server: {app.config['MAIL_SERVER']}")
        print(f"SMTP Port: {app.config['MAIL_PORT']}")
        print(f"Username: {app.config['MAIL_USERNAME']}")
        print(f"Using SSL: {app.config['MAIL_USE_SSL']}")
        print(f"Using TLS: {app.config['MAIL_USE_TLS']}")
        
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Создаем SMTP соединение в зависимости от настроек
        if app.config['MAIL_USE_SSL']:
            print("Creating SMTP_SSL connection...")
            server = smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        else:
            print("Creating SMTP connection...")
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            if app.config['MAIL_USE_TLS']:
                print("Starting TLS...")
                server.starttls()
        
        server.set_debuglevel(2)  # Максимальный уровень отладки
        
        print("Attempting login...")
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        print("Sending message...")
        server.send_message(msg)
        print("Message sent successfully!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {str(e)}")
        print("Please check:")
        print("1. Email address is correct")
        print("2. App password is correct (no spaces)")
        print("3. 2FA is enabled on your Google account")
        print("4. App password was generated for 'Mail' or 'Other'")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

@app.route('/quick_order', methods=['POST'])
@login_required
def quick_order():
    try:
        print("=== Начало создания быстрого заказа ===")
        data = request.get_json()
        print(f"Получены данные заказа: {data}")
        
        # Проверяем наличие всех необходимых полей
        required_fields = ['product_id', 'name', 'price', 'size', 'color', 'quantity', 
                         'customer_name', 'customer_email', 'customer_phone', 'payment_method', 'address']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"Отсутствуют обязательные поля: {missing_fields}")
            return jsonify({
                'success': False,
                'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
            }), 400

        # Проверяем формат email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['customer_email']):
            print(f"Неверный формат email: {data['customer_email']}")
            return jsonify({
                'success': False,
                'message': 'Неверный формат email'
            }), 400

        # Проверяем формат телефона
        phone_pattern = r'^\+?[0-9]{10,15}$'
        if not re.match(phone_pattern, data['customer_phone']):
            print(f"Неверный формат телефона: {data['customer_phone']}")
            return jsonify({
                'success': False,
                'message': 'Неверный формат телефона'
            }), 400

        # Проверяем наличие товара
        product = Product.query.get(data['product_id'])
        if not product:
            print(f"Товар не найден: {data['product_id']}")
            return jsonify({
                'success': False,
                'message': 'Товар не найден'
            }), 404

        # Проверяем доступное количество
        if product.stock < data['quantity']:
            print(f"Недостаточно товара: запрошено {data['quantity']}, доступно {product.stock}")
            return jsonify({
                'success': False,
                'message': 'Недостаточно товара'
            }), 400

        print("Создание нового заказа...")
        # Создаем новый заказ
        order = Order(
            user_id=current_user.id,  # Теперь всегда будет user_id
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            payment_method=data['payment_method'],
            status='pending',
            total_amount=data['price'] * data['quantity'],
            items=[{
                'name': data['name'],
                'price': data['price'],
                'quantity': data['quantity'],
                'size': data['size'],
                'color': data['color'],
                'total': data['price'] * data['quantity']
            }],
            customer_info={
                'name': data['customer_name'],
                'email': data['customer_email'],
                'phone': data['customer_phone'],
                'payment_method': data['payment_method'],
                'address': data['address']
            }
        )
        print(f"Заказ создан: {order.id}")

        # Создаем элемент заказа
        order_item = OrderItem(
            order=order,
            product=product,
            quantity=data['quantity'],
            price=data['price'],
            size=data['size'],
            color=data['color']
        )
        print(f"Элемент заказа создан: {order_item.id}")

        # Обновляем количество товара
        product.stock -= data['quantity']
        print(f"Количество товара обновлено: {product.stock}")

        # Сохраняем изменения
        db.session.add(order)
        db.session.add(order_item)
        db.session.commit()
        print("Изменения сохранены в базе данных")

        # Отправляем email клиенту
        try:
            print("Отправка email клиенту...")
            customer_email_body = f'''
            Спасибо за ваш заказ!
            
            Детали заказа №{order.id}:
            Товар: {data['name']}
            Размер: {data['size']}
            Цвет: {data['color']}
            Количество: {data['quantity']}
            Сумма: {data['price'] * data['quantity']} руб.
            
            Адрес доставки: {data['address']}
            
            Статус заказа: {order.status}
            
            Мы свяжемся с вами в ближайшее время для подтверждения заказа.
            '''
            
            if send_email_smtp(data['customer_email'], f'Подтверждение заказа №{order.id}', customer_email_body):
                print("Email клиенту успешно отправлен")
            else:
                print("Не удалось отправить email клиенту")

            # Отправляем уведомление администратору
            print("Отправка уведомления администратору...")
            admin_email_body = f'''
            Новый заказ №{order.id}!
            
            Детали заказа:
            Товар: {data['name']}
            Размер: {data['size']}
            Цвет: {data['color']}
            Количество: {data['quantity']}
            Сумма: {data['price'] * data['quantity']} руб.
            
            Информация о покупателе:
            Имя: {data['customer_name']}
            Email: {data['customer_email']}
            Телефон: {data['customer_phone']}
            Адрес: {data['address']}
            Способ оплаты: {data['payment_method']}
            '''
            
            if send_email_smtp(app.config['ADMIN_EMAIL'], f'Новый заказ №{order.id}', admin_email_body):
                print("Уведомление администратору успешно отправлено")
            else:
                print("Не удалось отправить уведомление администратору")
                
        except Exception as e:
            print(f"Ошибка при отправке email: {str(e)}")
            # Не прерываем процесс, если email не удалось отправить
            pass

        print("=== Заказ успешно создан ===")
        return jsonify({
            'success': True,
            'message': 'Заказ успешно создан',
            'order_id': order.id
        })

    except Exception as e:
        print(f"=== Ошибка при создании заказа: {str(e)} ===")
        print("Трейсбек ошибки:")
        import traceback
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Произошла ошибка при оформлении заказа. Попробуйте позже.'
        }), 500

def send_order_confirmation_email(email, order):
    try:
        # Формируем тему письма
        subject = f'Подтверждение заказа #{order.id}'
        
        # Формируем тело письма
        body = f"""
        Уважаемый покупатель!
        
        Спасибо за ваш заказ в нашем магазине. Мы получили ваш заказ и обработаем его в ближайшее время.
        
        Детали заказа:
        Номер заказа: #{order.id}
        Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}
        Статус: {order.status}
        
        Товары в заказе:
        """
        
        # Добавляем информацию о товарах
        for item in order.items:
            body += f"""
            - {item['name']}
              Размер: {item['size']}
              Цвет: {item['color']}
              Количество: {item['quantity']}
              Цена: {item['price']} грн
              Сумма: {item['total']} грн
            """
        
        body += f"""
        
        Общая сумма заказа: {order.total_amount} грн
        
        Мы свяжемся с вами в ближайшее время для подтверждения заказа.
        
        С уважением,
        Команда Cursor Shop
        """
        
        # Создаем объект сообщения
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body
        )
        
        # Отправляем письмо
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")
        return False

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)

print("Flask application for Cursor Clothing Shop is ready to run!")