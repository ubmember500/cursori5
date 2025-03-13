import sys
import os

# Добавляем путь к проекту
path = '/home/ubmember500/cursori5'
if path not in sys.path:
    sys.path.append(path)

# Настройки SMTP
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = 'defensivelox@gmail.com'
os.environ['MAIL_PASSWORD'] = 'pgqmxxglsrsscaue'
os.environ['MAIL_DEFAULT_SENDER'] = 'defensivelox@gmail.com'
os.environ['ADMIN_EMAIL'] = 'defensivelox@gmail.com'

# Импортируем Flask-приложение
from app import app as application

# PythonAnywhere использует это для запуска приложения
if __name__ == '__main__':
    application.run() 