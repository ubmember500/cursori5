import sys
import os

# Добавьте путь к вашему проекту
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Настройки email
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = 'defensivelox@gmail.com'
os.environ['MAIL_PASSWORD'] = 'pgqm xxgl srss caue'
os.environ['MAIL_DEFAULT_SENDER'] = 'defensivelox@gmail.com'
os.environ['ADMIN_EMAIL'] = 'defensivelox@gmail.com'

# Импортируем Flask-приложение
from app import app as application

# PythonAnywhere использует это для запуска приложения
if __name__ == '__main__':
    application.run() 