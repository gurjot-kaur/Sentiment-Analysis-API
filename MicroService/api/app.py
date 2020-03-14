import logging

from flask import Flask

logger = logging.getLogger(__name__)


def initialize_app():
    """Initializes a Flask app.

    Add configurations if needed.
    """
    app = Flask(__name__)
    from ml_deploy_demo.api.ml_app import ml_app

    app.register_blueprint(ml_app)
    return app
