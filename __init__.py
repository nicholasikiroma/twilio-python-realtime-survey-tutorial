from flask import Flask
from .views import ivr_phone_tree


def create_app():
    """Returns an instance of a Flask application"""
    app = Flask(__name__)
    app.register_blueprint(ivr_phone_tree, url_prefix="/survey")
    return app
