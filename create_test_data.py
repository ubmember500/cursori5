from app import app, db, User, Product, Category, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_data():
    with app.app_context():
        try:
            print("Создание тестовых данных...")
            
            # Проверяем, есть ли уже данные
            users = User.query.all()
            if users:
                print(f"В базе данных уже есть {len(users)} пользователей")
                return
            
            # Создаем тестового пользователя
            test_user = User(
                username="testuser",
                email="test@example.com",
                password_hash=generate_password_hash("password123"),
                first_name="Test",
                last_name="User",
                phone="+380123456789",
                address="Test Address",
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(test_user)
            db.session.flush()
            print(f"Создан тестовый пользователь: ID={test_user.id}, Username={test_user.username}")
            
            # Создаем тестовую категорию
            test_category = Category(
                name="Тестовая категория"
            )
            db.session.add(test_category)
            db.session.flush()
            print(f"Создана тестовая категория: ID={test_category.id}, Name={test_category.name}")
            
            # Создаем тестовый товар
            test_product = Product(
                name="Тестовый товар",
                description="Описание тестового товара",
                price=100.0,
                stock=10,
                category_id=test_category.id,
                image="test_product.jpg"
            )
            db.session.add(test_product)
            db.session.flush()
            print(f"Создан тестовый товар: ID={test_product.id}, Name={test_product.name}")
            
            # Создаем тестовый заказ
            test_order = Order(
                user_id=test_user.id,
                status="pending",
                total_amount=160.0,  # 100 + 60 (доставка)
                created_at=datetime.utcnow(),
                shipping_address="Тестовый адрес",
                shipping_city="Тестовый город",
                shipping_postal_code="12345",
                phone_number="+380123456789",
                payment_method="cash",
                messenger_contact=None
            )
            db.session.add(test_order)
            db.session.flush()
            print(f"Создан тестовый заказ: ID={test_order.id}, User_ID={test_order.user_id}")
            
            # Создаем тестовый элемент заказа
            test_order_item = OrderItem(
                order_id=test_order.id,
                product_id=test_product.id,
                quantity=1,
                price=100.0,
                size="M",
                color="Черный"
            )
            db.session.add(test_order_item)
            db.session.flush()
            print(f"Создан тестовый элемент заказа: ID={test_order_item.id}, Order_ID={test_order_item.order_id}")
            
            # Сохраняем изменения
            db.session.commit()
            print("Тестовые данные успешно созданы")
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании тестовых данных: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_test_data() 