# Vercel Serverless Function Bridge
# This file connects Vercel's entry point to your Flask application

try:
    # Everything is now inside the api/ folder for reliable Vercel bundling
    from .app import app
    application = app
except ImportError:
    # Normal import if running locally
    from app import app
    application = app
except Exception as e:
    from flask import Flask, jsonify
    application = Flask(__name__)
    @application.route('/api/<path:path>')
    @application.route('/api/')
    def error_route(path=None):
        return jsonify({
            "error": "Mono-repo Initialization Failed",
            "message": str(e),
            "hint": "Ensure app.py and models/ are correctly structured within the api/ directory."
        }), 500
