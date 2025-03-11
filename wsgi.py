import sys
import os

# Добавьте путь к вашему проекту
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Импортируем Flask-приложение
from app import app as application

# PythonAnywhere использует это для запуска приложения
if __name__ == '__main__':
    application.run() 