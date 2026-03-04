from datetime import datetime, timedelta
from .finnhub_client import get_client
from .config import get_key

def _range_days(days=60):
    to = datetime.utcnow()
    frm = to - timedelta(days=days)
    return int(frm.timestamp()), int(to.timestamp())

def fetch_price_series(symbol):
    cli = get_client()
    if cli:
        try:
            frm, to = _range_days(90)
            candles = cli.stock_candles(symbol, 'D', frm, to)
            ts = candles.get('t') or []
            closes = candles.get('c') or []
            series = []
            for i in range(min(len(ts), len(closes))):
                dt = datetime.utcfromtimestamp(ts[i]).strftime('%Y-%m-%d')
                series.append({'date': dt, 'close': float(closes[i])})
            return series
        except Exception:
            pass
    # Fallback demo series
    base = datetime.utcnow() - timedelta(days=30)
    series = []
    price = 100.0
    for i in range(30):
        d = (base + timedelta(days=i)).strftime('%Y-%m-%d')
        price += (1 if i % 2 == 0 else -0.5)
        series.append({'date': d, 'close': round(price, 2)})
    return series
