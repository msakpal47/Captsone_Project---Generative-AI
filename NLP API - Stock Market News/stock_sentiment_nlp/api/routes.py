from flask import Blueprint, jsonify, current_app
from ..api.config import get_key
from ..api.price_fetcher import fetch_price_series
from ..api.news_fetcher import fetch_news

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/ping', methods=['GET'])
def ping():
    ks = {'finnhub': bool(get_key('FINNHUB_API_KEY')), 'newsapi': bool(get_key('NEWS_API_KEY'))}
    return jsonify({'status': 'ok', 'key_status': ks})

@api.route('/test', methods=['GET'])
def test():
    ks = {'finnhub': bool(get_key('FINNHUB_API_KEY')), 'newsapi': bool(get_key('NEWS_API_KEY'))}
    news = fetch_news('AAPL')
    price = fetch_price_series('AAPL')
    return jsonify({'key_status': ks, 'news_count': len(news or []), 'price_points': len(price or [])})

@api.route('/routes', methods=['GET'])
def routes():
    app = current_app
    paths = sorted([str(r) for r in app.url_map.iter_rules()])
    return jsonify({'routes': paths})
