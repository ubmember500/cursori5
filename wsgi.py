import sys
import os
from cryptography.fernet import Fernet
import base64

# Функция для генерации ключа шифрования
def generate_key():
    return Fernet.generate_key()

# Функция для шифрования пароля
def encrypt_password(password, key):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

# Функция для дешифрования пароля
def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

# Генерируем ключ (в реальном приложении его нужно хранить безопасно)
ENCRYPTION_KEY = b'YOUR_ENCRYPTION_KEY_HERE'

# Настройка путей
project_path = '/home/ubmember500/cursori5'

# Шифруем пароль
encrypted_password = encrypt_password('snxltrpnzytrfrbl', ENCRYPTION_KEY)

# Настройки SMTP
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '465'  # Используем SSL порт
os.environ['MAIL_USE_SSL'] = 'True'
os.environ['MAIL_USE_TLS'] = 'False'
os.environ['MAIL_USERNAME'] = 'defensivelox@gmail.com'
os.environ['MAIL_PASSWORD'] = encrypted_password
os.environ['MAIL_DEFAULT_SENDER'] = 'defensivelox@gmail.com'
os.environ['ADMIN_EMAIL'] = 'defensivelox@gmail.com'

# Импортируем приложение Flask
from app import app

# PythonAnywhere использует это для запуска приложения
if __name__ == '__main__':
    app.run() 