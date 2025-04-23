from flask import Blueprint, jsonify
from data.sales_data import get_sales_data, get_prices_data

home_bp = Blueprint('home', __name__)

@home_bp.route('/api/home/sales', methods=['GET'])
def get_sales():
    data = get_sales_data()
    return jsonify(data)

@home_bp.route('/api/home/prices', methods=['GET'])
def get_prices():
    data = get_prices_data()
    return jsonify(data)