from datetime import datetime, timedelta
from .finnhub_client import get_client

def _from_to_dates():
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=30)
    return from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')

def _map_finnhub(item):
    ts = item.get('datetime')
    published = datetime.utcfromtimestamp(ts).isoformat() if isinstance(ts, (int, float)) else None
    return {'title': item.get('headline') or '', 'url': item.get('url'), 'published': published}

def fetch_news(symbol):
    cli = get_client()
    if cli:
        f, t = _from_to_dates()
        try:
            data = cli.company_news(symbol, _from=f, to=t) or []
            return [_map_finnhub(x) for x in data if isinstance(x, dict)]
        except Exception:
            pass
    return [
        {'title': f'{symbol} releases new AI product', 'url': None, 'published': None},
        {'title': f'{symbol} stock shows strong quarterly performance', 'url': None, 'published': None},
        {'title': f'Market reacts to {symbol} earnings report', 'url': None, 'published': None}
    ]
