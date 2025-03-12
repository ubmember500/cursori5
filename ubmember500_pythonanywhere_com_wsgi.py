import sys
import os

# Add your project path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import Flask application
from app import app as application

# PythonAnywhere uses this to run the application
if __name__ == '__main__':
    application.run() 