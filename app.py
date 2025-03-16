# from liqpay import LiqPay  # Temporarily commented out

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, make_response, jsonify, abort
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
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import bleach
import re
from sqlalchemy.exc import IntegrityError
from auth_middleware import login_required

# Загрузка переменных окружения
# load_dotenv()  # Убираем загрузку .env

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
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Устанавливаем секретный ключ напрямую
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

# Настройка почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'defensivelox@gmail.com'
app.config['MAIL_PASSWORD'] = 'pgqm xxgl srss caue'
app.config['MAIL_DEFAULT_SENDER'] = 'defensivelox@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True)
    data = db.Column(db.Text)
    expiry = db.Column(db.DateTime)


class Order(db.Model):
    __tablename__ = 'orders'  # Явно указываем имя таблицы
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Информация о доставке
    shipping_address = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    
    # Способ оплаты
    payment_method = db.Column(db.String(50))  # cash, card, bank_transfer
    
    # Связь с пользователем и товарами
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'  # Явно указываем имя таблицы
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Обновляем ссылку на таблицу orders
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Цена на момент заказа
    
    # Дополнительные параметры товара
    size = db.Column(db.String(10))
    color = db.Column(db.String(50))
    
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
        print(f"Применены фильтры по цене: {min_price} - {max_price}")
        
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
    action = request.form.get('action', 'cart')  # Получаем действие (cart или buy)

    # Получаем товар
    product = Product.query.get_or_404(product_id)
    
    # Проверяем наличие товара
    if quantity > product.stock:
        flash('Извините, данного количества товара нет в наличии', 'error')
        return redirect(request.referrer or url_for('products'))

    # Убеждаемся, что у нас есть изображение и оно в правильном формате
    if not image or image == 'None':
        image = get_random_product_image(product.category_id)
    elif not image.startswith('img/products/'):
        if '/' in image:
            image = image.split('/')[-1]
        image = f'img/products/{image}'

    # Проверяем, есть ли товар уже в корзине
    item_in_cart = False
    for item in cart:
        if item['id'] == product_id and item.get('size') == size and item.get('color') == color:
            if item['quantity'] + quantity > product.stock:
                flash('Извините, данного количества товара нет в наличии', 'error')
                return redirect(request.referrer or url_for('products'))
            item['quantity'] += quantity
            if not item.get('image') or item['image'] == 'None':
                item['image'] = image
            item_in_cart = True
            break

    # Если товара нет в корзине, добавляем его
    if not item_in_cart:
        cart.append({
            'id': product_id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'size': size,
            'color': color,
            'image': image
        })

    session.modified = True
    
    # Если действие "buy", перенаправляем на оформление заказа
    if action == 'buy':
        return redirect(url_for('checkout'))
        
    flash('Товар добавлен в корзину!', 'success')
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
    if not g.user:
        flash('Пожалуйста, войдите в систему для оформления заказа', 'warning')
        return redirect(url_for('login', next=url_for('checkout')))
    
    # Проверяем, есть ли товары в корзине
    if 'cart' not in session or not session['cart']:
        # Проверяем, есть ли параметр buy_now и product_id
        product_id = request.args.get('product_id')
        if product_id:
            # Получаем информацию о продукте
            product = Product.query.get(product_id)
            if product:
                # Получаем размер, цвет и количество из параметров запроса
                size = request.args.get('size', '')
                color = request.args.get('color', '')
                quantity = int(request.args.get('quantity', 1))
                
                # Создаем временную корзину для прямой покупки
                session['cart'] = [{
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'image': product.image,
                    'size': size,
                    'color': color
                }]
                session.modified = True
            else:
                flash('Товар не найден', 'error')
                return redirect(url_for('products'))
        else:
            flash('Ваша корзина пуста', 'warning')
            return redirect(url_for('products'))
    
    # Получаем товары из корзины
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['id'])
        if product:
            item_total = item['price'] * item['quantity']
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'total': item_total,
                'image': item.get('image'),
                'size': item.get('size'),
                'color': item.get('color')
            })
            total += item_total
    
    # Добавляем стоимость доставки
    delivery_cost = 60.00
    total_with_delivery = total + delivery_cost
    
    if request.method == 'POST':
        # Получаем данные из формы
        phone_number = request.form.get('phone_number')
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city')
        shipping_postal_code = request.form.get('shipping_postal_code')
        payment_method = request.form.get('payment_method')
        messenger_contact = request.form.get('messenger_contact', '')
        email = request.form.get('email')
        
        # Проверяем обязательные поля
        if not phone_number or not shipping_address or not shipping_city or not payment_method:
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, delivery_cost=delivery_cost, total_with_delivery=total_with_delivery)
        
        # Проверяем, что для оплаты картой указан контакт в мессенджере
        if payment_method == 'card' and not messenger_contact:
            flash('Для оплаты картой необходимо указать контакт в Telegram/Viber', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, delivery_cost=delivery_cost, total_with_delivery=total_with_delivery)
        
        try:
            # Создаем новый заказ
            order = Order(
                user_id=g.user.id,
                status='pending',
                total_amount=total_with_delivery,
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_postal_code=shipping_postal_code,
                phone_number=phone_number,
                payment_method=payment_method,
                messenger_contact=messenger_contact if payment_method == 'card' else None
            )
            
            db.session.add(order)
            db.session.flush()  # Получаем ID заказа
            
            # Добавляем товары в заказ
            for item in session['cart']:
                product = Product.query.get(item['id'])
                if product:
                    # Проверяем наличие товара на складе
                    if product.stock < item['quantity']:
                        flash(f'Извините, товара "{product.name}" недостаточно на складе. В наличии: {product.stock}', 'error')
                        return render_template('checkout.html', cart_items=cart_items, total=total, delivery_cost=delivery_cost, total_with_delivery=total_with_delivery)
                    
                    # Уменьшаем количество товара на складе
                    product.stock -= item['quantity']
                    
                    # Добавляем товар в заказ
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=item['quantity'],
                        price=item['price'],
                        size=item.get('size'),
                        color=item.get('color')
                    )
                    db.session.add(order_item)
            
            db.session.commit()
            
            # Очищаем корзину
            session['cart'] = []
            session.modified = True
            
            # Отправляем email с подтверждением
            try:
                # Используем email из формы, если он есть, иначе email пользователя
                recipient_email = email if email else g.user.email
                
                msg = Message(
                    'Подтверждение заказа',
                    sender='defensivelox@gmail.com',
                    recipients=[recipient_email]
                )
                
                # Добавляем информацию о доставке в текст письма
                delivery_info = "Стоимость доставки: 60.00 ₴"
                
                msg.body = f'''
                Спасибо за ваш заказ!
                
                Номер заказа: {order.id}
                Сумма товаров: {total} ₴
                {delivery_info}
                Итого к оплате: {total_with_delivery} ₴
                Статус: В обработке
                
                Адрес доставки:
                {shipping_address}
                {shipping_city}
                {shipping_postal_code}
                
                Способ оплаты: {payment_method}
                
                Мы свяжемся с вами по телефону {phone_number} для подтверждения заказа.
                '''
                mail.send(msg)
                print(f"Email с подтверждением отправлен на {recipient_email}")
                
                # Отправляем копию администратору
                admin_msg = Message(
                    f'Новый заказ #{order.id}',
                    sender='defensivelox@gmail.com',
                    recipients=['defensivelox@gmail.com']
                )
                
                admin_msg.body = f'''
                Новый заказ от пользователя {g.user.username} ({recipient_email})!
                
                Номер заказа: {order.id}
                Сумма товаров: {total} ₴
                {delivery_info}
                Итого к оплате: {total_with_delivery} ₴
                
                Адрес доставки:
                {shipping_address}
                {shipping_city}
                {shipping_postal_code}
                
                Способ оплаты: {payment_method}
                Телефон: {phone_number}
                '''
                
                if payment_method == 'card' and messenger_contact:
                    admin_msg.body += f'\nКонтакт в мессенджере: {messenger_contact}'
                
                mail.send(admin_msg)
                print(f"Email с уведомлением о заказе отправлен администратору")
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
            
            flash('Заказ успешно оформлен! Мы отправили подтверждение на ваш email.', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при оформлении заказа: {e}")
            import traceback
            traceback.print_exc()
            flash('Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.', 'danger')
            return render_template('checkout.html', cart_items=cart_items, total=total, delivery_cost=delivery_cost, total_with_delivery=total_with_delivery)
    
    return render_template('checkout.html', cart_items=cart_items, total=total, delivery_cost=delivery_cost, total_with_delivery=total_with_delivery)


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
            # Создаем объект сообщения
            msg = Message(
                subject=f'Новое сообщение от {name}: {subject}',
                recipients=['defensivelox@gmail.com'],
                body=email_body
            )
            
            # Отправляем email асинхронно
            Thread(target=send_async_email, args=(app, msg)).start()
            
            flash('Ваше сообщение успешно отправлено!', 'success')
        except Exception as e:
            print(f"Ошибка создания сообщения: {e}")
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
        
        print(f"Попытка регистрации: username={username}, email={email}")  # Добавляем лог
        
        # Проверяем, что пароли совпадают
        if password != confirm_password:
            print("Пароли не совпадают")  # Добавляем лог
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('register'))
        
        # Проверяем, что пользователь с таким email или username еще не существует
        if User.query.filter_by(username=username).first():
            print(f"Пользователь с именем {username} уже существует")  # Добавляем лог
            flash('Пользователь с таким именем уже существует!', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            print(f"Пользователь с email {email} уже существует")  # Добавляем лог
            flash('Пользователь с таким email уже существует!', 'danger')
            return redirect(url_for('register'))
        
        try:
            # Создаем нового пользователя
            user = User(username=username, email=email)
            user.set_password(password)
            print(f"Создаем нового пользователя: {username}")  # Добавляем лог
            
            db.session.add(user)
            db.session.commit()
            print(f"Пользователь {username} успешно создан")  # Добавляем лог
            
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании пользователя: {str(e)}")  # Добавляем лог
            flash('Произошла ошибка при регистрации. Попробуйте позже.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Сохраняем ID пользователя в сессии
            session.clear()
            session['user_id'] = user.id
            
            # Перенаправляем на запрошенную страницу или на главную
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            
            return redirect(next_page)
        
        flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
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
                # Отправляем email
                reset_url = url_for('reset_password', token=token, _external=True)
                msg = Message('Восстановление пароля',
                            sender='defensivelox@gmail.com',
                            recipients=[email])
                msg.body = f'Для восстановления пароля перейдите по ссылке: {reset_url}'
                mail.send(msg)
                
                flash('Инструкции по восстановлению пароля отправлены на ваш email', 'success')
                return redirect(url_for('login'))
            except Exception as e:
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

# Добавляем before_request для проверки пользователя перед каждым запросом
@app.before_request
def before_request():
    """
    Выполняется перед каждым запросом.
    Загружает информацию о пользователе из сессии.
    """
    from auth_middleware import load_logged_in_user
    load_logged_in_user()

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

@app.before_request
def load_user_data():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        user = User.query.get(user_id)
        if user is None:
            g.user = None
            session.clear()
        else:
            g.user = user
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
    
    # Инициализируем корзину
    if 'cart' not in session:
        session['cart'] = []

# Обработчики ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    flash('Размер загружаемого файла превышает допустимый', 'error')
    return redirect(request.referrer or url_for('home'))

# Конфигурация безопасности
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Валидация email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    if not g.user:
        return redirect(url_for('login'))
        
    order = Order.query.get_or_404(order_id)
    
    # Проверяем, принадлежит ли заказ текущему пользователю
    if order.user_id != g.user.id:
        abort(403)
        
    return render_template('order_confirmation.html', order=order)

@app.route('/my-orders')
@login_required
def my_orders():
    """Display all orders for the currently logged-in user"""
    try:
        # Получаем все заказы пользователя, отсортированные по дате (новые сверху)
        orders = Order.query.filter_by(user_id=g.user.id).order_by(Order.created_at.desc()).all()
        
        # Для каждого заказа предварительно загружаем данные
        for order in orders:
            # Принудительно загружаем элементы заказа
            order.items_count = len(order.items)
            
            # Вычисляем общее количество товаров
            order.total_items = sum(item.quantity for item in order.items)
            
            # Форматируем статус для отображения
            if order.status == 'pending':
                order.status_display = 'Ожидает оплаты'
            elif order.status == 'paid':
                order.status_display = 'Оплачен'
            elif order.status == 'shipped':
                order.status_display = 'Отправлен'
            elif order.status == 'delivered':
                order.status_display = 'Доставлен'
            elif order.status == 'cancelled':
                order.status_display = 'Отменен'
            else:
                order.status_display = order.status
        
        return render_template('my_orders.html', orders=orders)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash('Произошла ошибка при загрузке заказов. Попробуйте позже.', 'error')
        return render_template('my_orders.html', orders=[], 
                              error_message="Не удалось загрузить ваши заказы. Возможно, вы еще не сделали ни одного заказа или произошла техническая ошибка.")

@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    """Display detailed information about a specific order"""
    try:
        # Получаем заказ и проверяем, принадлежит ли он текущему пользователю
        order = Order.query.get_or_404(order_id)
        if order.user_id != g.user.id:
            abort(403)  # Forbidden - пользователь не владеет этим заказом
        
        return render_template('order_details.html', order=order)
    except Exception as e:
        import traceback
        print(f"Ошибка при загрузке заказа {order_id}: {str(e)}")
        traceback.print_exc()
        flash('Произошла ошибка при загрузке заказа', 'danger')
        return redirect(url_for('my_orders'))

@app.route('/cancel-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def cancel_order(order_id):
    """Отмена заказа пользователем"""
    try:
        # Получаем заказ
        order = Order.query.get_or_404(order_id)
        
        # Проверяем, принадлежит ли заказ текущему пользователю
        if order.user_id != g.user.id:
            flash('У вас нет доступа к этому заказу', 'danger')
            return redirect(url_for('my_orders'))
        
        # Проверяем, можно ли отменить заказ (только в статусе "pending")
        if order.status != 'pending':
            flash('Этот заказ нельзя отменить, так как он уже обрабатывается или доставлен', 'warning')
            return redirect(url_for('order_details', order_id=order_id))
        
        # Меняем статус заказа на "cancelled"
        order.status = 'cancelled'
        
        # Возвращаем товары на склад
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity
                print(f"Возвращено на склад: {item.quantity} шт. товара {product.name}")
        
        db.session.commit()
        flash('Заказ успешно отменен', 'success')
        
        # Отправляем уведомление на email
        try:
            # Получаем пользователя
            user = User.query.get(order.user_id)
            
            # Отправляем уведомление клиенту
            msg = Message(
                'Отмена заказа',
                sender='defensivelox@gmail.com',
                recipients=[user.email]
            )
            msg.body = f'''
            Ваш заказ #{order.id} был отменен.
            
            Если у вас есть вопросы, пожалуйста, свяжитесь с нами.
            '''
            mail.send(msg)
            print(f"Email с уведомлением об отмене отправлен на {user.email}")
            
            # Отправляем уведомление администратору
            admin_msg = Message(
                f'Отмена заказа #{order.id}',
                sender='defensivelox@gmail.com',
                recipients=['defensivelox@gmail.com']
            )
            admin_msg.body = f'''
            Заказ #{order.id} от пользователя {user.username} ({user.email}) был отменен.
            
            Детали заказа:
            Сумма: {order.total_amount} ₴
            Адрес доставки: {order.shipping_address}, {order.shipping_city}
            Телефон: {order.phone_number}
            '''
            mail.send(admin_msg)
            print(f"Email с уведомлением об отмене заказа отправлен администратору")
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
        
        return redirect(url_for('my_orders'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при отмене заказа {order_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Произошла ошибка при отмене заказа. Попробуйте позже.', 'danger')
        return redirect(url_for('my_orders'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)

print("Flask application for Cursor Clothing Shop is ready to run!")
print("Flask application for Cursor Clothing Shop is ready to run!")