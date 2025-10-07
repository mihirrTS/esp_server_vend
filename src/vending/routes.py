from flask import Blueprint, render_template, request, jsonify

vending_bp = Blueprint('vending', __name__)

@vending_bp.route('/')
def index():
    return render_template('index.html')

@vending_bp.route('/vend', methods=['POST'])
def vend():
    item_id = request.form.get('item_id')
    # Simulate vending logic here
    if item_id:
        message = f'Vending item {item_id}'
        return jsonify({'message': message}), 200
    return jsonify({'message': 'Item not found'}), 400