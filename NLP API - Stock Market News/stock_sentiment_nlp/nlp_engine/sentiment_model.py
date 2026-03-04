import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

def _get_sia():
    try:
        return SentimentIntensityAnalyzer()
    except:
        nltk.download('vader_lexicon')
        return SentimentIntensityAnalyzer()

def _label(compound):
    if compound > 0.05:
        return 'Positive'
    if compound < -0.05:
        return 'Negative'
    return 'Neutral'

def analyze_sentiments(texts, original_texts=None):
    sia = _get_sia()
    inputs = original_texts if original_texts else texts
    scores = []
    counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for text in inputs:
        sc = sia.polarity_scores(text or '')
        label = _label(sc['compound'])
        scores.append({'text': text, 'compound': sc['compound'], 'label': label})
        counts[label] += 1
    return {'counts': counts, 'scores': scores}
