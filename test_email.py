from app import app, send_async_email
from flask_mail import Message
from threading import Thread
import sys

# Создаем тестовое сообщение
with app.app_context():
    try:
        print("Начинаю тестирование отправки email...")
        
        # Пароль передается как аргумент командной строки
        if len(sys.argv) > 1:
            custom_password = sys.argv[1]
            print(f"Получен пароль из аргументов командной строки")
        else:
            # Используем пароль из конфигурации
            custom_password = None
            print("Используется пароль из конфигурации приложения")
        
        msg = Message(
            'Тестовое сообщение от Cursor Shop с русским текстом',
            sender='defensivelox@gmail.com',
            recipients=['defensivelox@gmail.com']
        )
        msg.body = '''
        Это тестовое сообщение для проверки работы отправки email.
        
        Проверка поддержки русского языка:
        Привет, мир! Как дела? Это тестовое сообщение с русским текстом.
        
        С уважением,
        Команда Cursor Shop
        '''
        
        # Отправляем асинхронно с пользовательским паролем
        Thread(target=send_async_email, args=(app, msg, custom_password)).start()
        
        print("Запущена асинхронная отправка тестового email")
        print("Проверьте логи для получения информации о результате отправки")
        
    except Exception as e:
        print(f"Ошибка при отправке тестового сообщения: {str(e)}")
        import traceback
        traceback.print_exc() 