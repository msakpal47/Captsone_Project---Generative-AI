# AI Stock News Sentiment Analyzer

## Overview
Analyze recent news for a stock ticker and visualize sentiment and trends. The app serves a simple web UI and JSON APIs built with Flask. News and prices are fetched via Finnhub when a key is present; otherwise demo data keeps the UI functional.

## Key Features
- Enter a ticker or choose from a list to analyze news sentiment.
- VADER-based sentiment analysis with Positive/Negative/Neutral counts.
- Trend and price charts rendered with Chart.js.
- Local config storage for FINNHUB_API_KEY.

## Project Structure
- Backend: `stock_sentiment_nlp/app.py` (Flask app, routes, rendering)
- Data fetchers: `stock_sentiment_nlp/api/news_fetcher.py`, `stock_sentiment_nlp/api/price_fetcher.py`
- NLP: `stock_sentiment_nlp/nlp_engine/` (preprocess, sentiment model)
- UI: `stock_sentiment_nlp/templates/index.html`, `stock_sentiment_nlp/static/`
- Config & results: `stock_sentiment_nlp/data/config.json`, `stock_sentiment_nlp/results/`
- Entrypoint: `server.py`

## Setup
1. Install Python 3.10+ and pip.
2. Install dependencies:
   - `python -m pip install -r stock_sentiment_nlp/requirements.txt`
3. (Optional) Add your Finnhub API key:
   - Run the app and submit the key via the form, or set env var `FINNHUB_API_KEY`.

## Run
Choose one:
- `python server.py`
- `python -m flask --app stock_sentiment_nlp.app run --host 127.0.0.1 --port 5000`

Visit: `http://127.0.0.1:5000`

## API Endpoints
- `GET /` – Render UI
- `POST /` – Analyze selected/custom ticker
- `POST /set_key` – Save `FINNHUB_API_KEY` locally
- `GET /api/ping` – Health + key status
- `GET /api/test` – Quick data check (counts for AAPL)
- `GET /api/routes` – List registered routes

## Notes
- NewsAPI has been removed. Finnhub is primary; when absent, the app uses sample news and a demo price series.
- Local results are saved under `stock_sentiment_nlp/results/` per run.

## Quick Verify
- `python -m stock_sentiment_nlp._route_test` – checks `/api/test`
- `python -m stock_sentiment_nlp._verify` – runs NLP and data fetch pipeline

## Summary CSV
See `project_summary.csv` for a one-glance overview of components and responsibilities.
