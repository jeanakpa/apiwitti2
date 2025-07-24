#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Ensure all directories are in the Python path
for root, dirs, files in os.walk(current_dir):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        if dir_path not in sys.path:
            sys.path.insert(0, dir_path)

# Import the Flask app from application.py to avoid conflict with gunicorn.app
from application import app

if __name__ == "__main__":
    # Pour le développement local
    app.run(debug=app.config.get('DEBUG', False)) 