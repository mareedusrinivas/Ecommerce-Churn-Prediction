import os
import sys

# Add root directory to path so we can import app.py and other modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from app import app
    application = app
except Exception as e:
    from flask import Flask, jsonify
    application = Flask(__name__)
    @application.route('/api/<path:path>')
    @application.route('/api/')
    def error_route(path=None):
        return jsonify({
            "error": "Backend Initialization Failed",
            "message": str(e),
            "hint": "Check if all dependencies are in requirements.txt and models exist."
        }), 500
