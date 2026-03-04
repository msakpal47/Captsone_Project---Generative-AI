from .app import app
from .nlp_engine.sentiment_model import analyze_sentiments
from .api.news_fetcher import fetch_news
from .api.price_fetcher import fetch_price_series

texts = ["Stocks rally on earnings beat", "Market crashes amid recession fears", "Company announces new product launch"]
result = analyze_sentiments(texts)
print("Sentiment counts:", result["counts"])

news = fetch_news("AAPL")
print("Fetched articles:", len(news))

price = fetch_price_series("AAPL")
print("Price points:", len(price))

print("Import OK")
