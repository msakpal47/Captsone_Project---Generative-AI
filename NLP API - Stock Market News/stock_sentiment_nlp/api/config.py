import os
import json

def _base_dir():
    return os.path.dirname(os.path.dirname(__file__))

def _config_paths():
    base = os.path.join(_base_dir(), 'data')
    return [
        os.path.join(base, 'config.json'),
        os.path.join(base, 'config.jason'),
    ]

def load_config():
    for path in _config_paths():
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f) or {}
                    return data
            except Exception:
                continue
    return {}

def save_config(cfg):
    os.makedirs(os.path.join(_base_dir(), 'data'), exist_ok=True)
    path = _config_paths()[0]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f)

def get_key(name):
    env = os.getenv(name)
    if env:
        return env
    cfg = load_config()
    if name in cfg and cfg[name]:
        return cfg[name]
    alt = {
        'FINNHUB_API_KEY': ['finnhub_api_key', 'finnhubKey', 'finnhub', 'api_key'],
    }
    for k in alt.get(name, []):
        v = cfg.get(k)
        if v:
            return v
    return None

def set_key(name, value):
    cfg = load_config()
    cfg[name] = value
    save_config(cfg)
