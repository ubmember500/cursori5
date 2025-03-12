import sys
import os

# Add your project path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Set the path to the SQLite database
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(path, 'instance', 'cursor_shop.db')

# Import Flask application
from app import app as application

# PythonAnywhere uses this to run the application
if __name__ == '__main__':
    application.run() 