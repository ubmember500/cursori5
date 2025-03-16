from app import app, db, Order, OrderItem, Product, User
import traceback
import sys

def debug_checkout(user_id, cart_items, form_data):
    with app.app_context():
        try:
            print(f"Отладка функции checkout для пользователя {user_id}")
            
            # Получаем пользователя
            user = User.query.get(user_id)
            if not user:
                print(f"Ошибка: пользователь с ID {user_id} не найден")
                return
            
            print(f"Пользователь: {user.username}, {user.email}")
            
            # Проверяем товары в корзине
            total = 0
            valid_cart_items = []
            
            for item in cart_items:
                product = Product.query.get(item['id'])
                if product:
                    item_total = item['price'] * item['quantity']
                    valid_cart_items.append({
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
                    print(f"Товар {product.name} (ID: {product.id}) добавлен в корзину, цена: {item['price']}, количество: {item['quantity']}")
                else:
                    print(f"Ошибка: товар с ID {item['id']} не найден")
            
            if not valid_cart_items:
                print("Ошибка: корзина пуста после проверки товаров")
                return
            
            # Добавляем стоимость доставки
            delivery_cost = 60.00
            total_with_delivery = total + delivery_cost
            print(f"Общая сумма товаров: {total}, с доставкой: {total_with_delivery}")
            
            # Проверяем обязательные поля формы
            required_fields = ['phone_number', 'shipping_address', 'shipping_city', 'payment_method']
            for field in required_fields:
                if not form_data.get(field):
                    print(f"Ошибка: отсутствует обязательное поле {field}")
                    return
            
            # Проверяем, что для оплаты картой указан контакт в мессенджере
            if form_data.get('payment_method') == 'card' and not form_data.get('messenger_contact'):
                print("Ошибка: для оплаты картой необходимо указать контакт в Telegram/Viber")
                return
            
            # Создаем заказ
            try:
                order = Order(
                    user_id=user.id,
                    status='pending',
                    total_amount=total_with_delivery,
                    shipping_address=form_data.get('shipping_address'),
                    shipping_city=form_data.get('shipping_city'),
                    shipping_postal_code=form_data.get('shipping_postal_code', ''),
                    phone_number=form_data.get('phone_number'),
                    payment_method=form_data.get('payment_method'),
                    messenger_contact=form_data.get('messenger_contact') if form_data.get('payment_method') == 'card' else None
                )
                
                db.session.add(order)
                db.session.flush()  # Получаем ID заказа
                print(f"Создан заказ с ID {order.id}")
                
                # Добавляем товары в заказ
                for item in valid_cart_items:
                    product = Product.query.get(item['id'])
                    if product:
                        # Проверяем наличие товара на складе
                        if product.stock < item['quantity']:
                            db.session.rollback()
                            print(f"Ошибка: товара {product.name} недостаточно на складе. В наличии: {product.stock}")
                            return
                        
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
                        print(f"Добавлен товар {product.name} в заказ {order.id}")
                
                # Не делаем commit, чтобы не изменять базу данных
                # db.session.commit()
                db.session.rollback()
                print("Заказ успешно создан (симуляция, изменения отменены)")
                
            except Exception as e:
                db.session.rollback()
                print(f"Ошибка при создании заказа: {e}")
                traceback.print_exc(file=sys.stdout)
                
        except Exception as e:
            print(f"Ошибка при отладке функции checkout: {e}")
            traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    # Тестовые данные
    user_id = 1  # ID существующего пользователя
    
    # Тестовая корзина
    cart_items = [
        {
            'id': 11,  # ID существующего товара (созданного в create_test_data.py)
            'name': 'Тестовый товар',
            'price': 100.0,
            'quantity': 1,
            'image': 'test_product.jpg',
            'size': 'M',
            'color': 'Черный'
        }
    ]
    
    # Тестовые данные формы
    form_data = {
        'phone_number': '+380123456789',
        'shipping_address': 'Тестовый адрес',
        'shipping_city': 'Тестовый город',
        'shipping_postal_code': '12345',
        'payment_method': 'cash',
        'email': 'test@example.com'
    }
    
    # Запускаем отладку
    debug_checkout(user_id, cart_items, form_data) 