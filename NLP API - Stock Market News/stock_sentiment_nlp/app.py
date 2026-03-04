from flask import Flask, render_template, request, jsonify
import os
import json
from .api.news_fetcher import fetch_news
from .api.price_fetcher import fetch_price_series
from .api.config import get_key, set_key
from .nlp_engine.preprocess import preprocess_texts
from .nlp_engine.sentiment_model import analyze_sentiments
 

app = Flask(__name__, template_folder='templates', static_folder='static')

 

TICKERS = ["AAPL","TSLA","MSFT","AMZN","GOOGL","GOOG","NVDA","META","NFLX","AMD","INTC","JPM","BAC","WFC","V","MA"]

def ensure_dirs():
    base = os.path.dirname(__file__)
 
@app.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({'status': 'ok', 'key_status': {'finnhub': bool(get_key('FINNHUB_API_KEY'))}})
 
@app.route('/api/test', methods=['GET'])
def api_test():
    ks = {'finnhub': bool(get_key('FINNHUB_API_KEY'))}
    news = fetch_news('AAPL')
    price = fetch_price_series('AAPL')
    return jsonify({'key_status': ks, 'news_count': len(news or []), 'price_points': len(price or [])})
 
@app.route('/api/routes', methods=['GET'])
def api_routes():
    paths = sorted([str(r) for r in app.url_map.iter_rules()])
    return jsonify({'routes': paths})

@app.route('/hello', methods=['GET'])
def _hello():
    return 'hello'
@app.route('/', methods=['GET', 'POST'])
def index():
    ensure_dirs()
    if request.method == 'GET':
        q_ping = (request.args.get('ping') or '').strip()
        q_test = (request.args.get('test') or '').strip()
        q_routes = (request.args.get('routes') or '').strip()
        if q_ping == '1':
            return jsonify({'status': 'ok', 'key_status': {'finnhub': bool(get_key('FINNHUB_API_KEY'))}})
        if q_test == '1':
            news = fetch_news('AAPL')
            price = fetch_price_series('AAPL')
            return jsonify({'key_status': {'finnhub': bool(get_key('FINNHUB_API_KEY'))},
                            'news_count': len(news or []), 'price_points': len(price or [])})
        if q_routes == '1':
            paths = sorted([str(r) for r in app.url_map.iter_rules()])
            return jsonify({'routes': paths})
    if request.method == 'GET':
        if (request.args.get('ping') or '').strip() == '1':
            return jsonify({'status': 'ok', 'key_status': {'finnhub': bool(get_key('FINNHUB_API_KEY'))}})
        if (request.args.get('test') or '').strip() == '1':
            news = fetch_news('AAPL')
            price = fetch_price_series('AAPL')
            return jsonify({'key_status': {'finnhub': bool(get_key('FINNHUB_API_KEY'))},
                            'news_count': len(news or []), 'price_points': len(price or [])})
        if (request.args.get('routes') or '').strip() == '1':
            paths = sorted([str(r) for r in app.url_map.iter_rules()])
            return jsonify({'routes': paths})
    symbol = ''
    symbol_select = ''
    articles = []
    counts = None
    scores = None
    dataset = None
    percents = None
    trend = None
    price = None
    key_status = {'finnhub': bool(get_key('FINNHUB_API_KEY'))}
    if request.method == 'POST':
        sym_select = (request.form.get('symbol_select') or '').strip().upper()
        symbol_select = sym_select
        if sym_select and sym_select != '_CUSTOM':
            symbol = sym_select
        else:
            symbol = (request.form.get('symbol') or '').strip().upper()
        if symbol == '_ALL':
            merged = []
            for t in TICKERS:
                arr = fetch_news(t)
                for it in arr:
                    it['ticker'] = t
                merged.extend(arr)
            articles = merged
            texts = [a['title'] for a in articles]
            processed = preprocess_texts(texts)
            result = analyze_sentiments(processed, original_texts=texts)
            counts = result['counts']
            scores = result['scores']
            dataset = counts
            out_path = os.path.join(os.path.dirname(__file__), 'results', 'analysis_ALL.json')
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'symbol': 'ALL', 'counts': counts, 'scores': scores, 'articles': articles}, f)
        elif symbol:
            articles = fetch_news(symbol)
            for it in articles:
                it['ticker'] = symbol
            texts = [a['title'] for a in articles]
            processed = preprocess_texts(texts)
            result = analyze_sentiments(processed, original_texts=texts)
            counts = result['counts']
            scores = result['scores']
            dataset = counts
            out_path = os.path.join(os.path.dirname(__file__), 'results', f'analysis_{symbol}.json')
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'symbol': symbol, 'counts': counts, 'scores': scores, 'articles': articles}, f)
    total = (counts['Positive'] + counts['Negative'] + counts['Neutral']) if (isinstance(counts, dict) and all(k in counts for k in ('Positive','Negative','Neutral'))) else 0
    if total:
        percents = {
            'Positive': round(100.0 * counts['Positive'] / total, 1),
            'Negative': round(100.0 * counts['Negative'] / total, 1),
            'Neutral': round(100.0 * counts['Neutral'] / total, 1),
        }
    def _build_trend(articles, scores):
        if not articles or not scores: return None
        by_day = {}
        for i in range(len(articles)):
            pub = articles[i].get('published') or ''
            day = (pub[:10] if len(pub) >= 10 else 'Unknown')
            lab = scores[i]['label']
            m = by_day.setdefault(day, {'Positive':0,'Negative':0,'Neutral':0})
            m[lab] += 1
        labels = sorted([d for d in by_day.keys() if d != 'Unknown'])
        pos = [by_day[d]['Positive'] for d in labels]
        neg = [by_day[d]['Negative'] for d in labels]
        neu = [by_day[d]['Neutral'] for d in labels]
        return {'labels': labels, 'pos': pos, 'neg': neg, 'neu': neu}
    trend = _build_trend(articles, scores)
    if symbol and symbol != '_ALL':
        price = fetch_price_series(symbol)
    return render_template('index.html',
                           symbol=symbol,
                           symbol_select=symbol_select,
                           tickers=TICKERS,
                           articles=articles,
                           counts=counts,
                           percents=percents,
                           scores=scores,
                           dataset=dataset,
                           trend=trend,
                           price=price,
                           key_status=key_status)

@app.route('/set_key', methods=['POST'])
def set_key_route():
    value = (request.form.get('api_key') or '').strip()
    if value:
        set_key('FINNHUB_API_KEY', value)
    return render_template('index.html', symbol='', symbol_select='', tickers=TICKERS, articles=[], counts=None, percents=None, scores=None, dataset=None, trend=None, price=None, key_status={'finnhub': bool(get_key('FINNHUB_API_KEY'))})

# API routes are registered via blueprint

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
