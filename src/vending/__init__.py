# Contents of /flask-vending-machine/flask-vending-machine/src/vending/__init__.py

from flask import Blueprint

vending_bp = Blueprint('vending', __name__)

from . import routes  # Import routes to register them with the blueprint