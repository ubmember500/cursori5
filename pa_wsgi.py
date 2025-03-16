import sys
import os

# Add your project path
path = '/home/ubmember500/cursori5'
if path not in sys.path:
    sys.path.append(path)

# Set the path to the SQLite database
INSTANCE_DIR = os.path.join(path, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR, mode=0o777)

os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(INSTANCE_DIR, "shop.db")}'

# Set Flask environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import Flask application
from app import app as application

# PythonAnywhere uses this to run the application
if __name__ == '__main__':
    application.run() 