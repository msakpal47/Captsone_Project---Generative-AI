import finnhub
from .config import get_key

def get_client():
    api_key = get_key('FINNHUB_API_KEY')
    if not api_key:
        return None
    try:
        return finnhub.Client(api_key=api_key)
    except Exception:
        return None
