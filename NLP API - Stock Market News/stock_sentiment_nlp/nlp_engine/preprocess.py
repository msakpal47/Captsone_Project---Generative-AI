import re

def preprocess_texts(texts):
    cleaned = []
    for t in texts:
        s = (t or '').lower()
        s = re.sub(r'[^a-z0-9\s]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        cleaned.append(s)
    return cleaned
