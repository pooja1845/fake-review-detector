"""
Fake Review Detection Engine
Uses NLP features + heuristic scoring to classify reviews
"""

import nltk
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")
import re
import math
from collections import Counter
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


# ─── Fake pattern dictionaries ───────────────────────────────────────────────

GENERIC_SUPERLATIVES = [
    "best ever", "worst ever", "absolutely amazing", "totally awesome",
    "highly recommend", "must buy", "life changing", "game changer",
    "perfect product", "love love love", "hate hate hate", "do not buy",
    "waste of money", "worth every penny", "exceeded expectations",
    "blew my mind", "beyond expectations", "five stars", "one star",
    "zero stars", "100%", "perfect", "flawless"
]

BOT_PHRASES = [
    "i received this product for free",
    "i was given this product",
    "disclaimer",
    "in exchange for",
    "honest review",
    "unbiased review",
    "i got this for",
    "complimentary",
    "sponsored"
]

FILLER_OPENERS = [
    "this product is", "this item is", "the product is",
    "i bought this", "i ordered this", "i purchased this"
]

STOP_WORDS = set(stopwords.words('english'))


# ─── Feature Extractors ───────────────────────────────────────────────────────

def caps_ratio(text: str) -> float:
    """Ratio of uppercase letters (excluding spaces/punctuation)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def exclamation_density(text: str) -> float:
    """Exclamation marks per sentence."""
    sentences = sent_tokenize(text)
    if not sentences:
        return 0.0
    return text.count('!') / len(sentences)


def repetition_score(text: str) -> float:
    """Detects repeated phrases/words (sign of bot-generated content)."""
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha() and w not in STOP_WORDS]
    if len(words) < 5:
        return 0.0
    freq = Counter(words)
    most_common_count = freq.most_common(1)[0][1] if freq else 0
    return most_common_count / len(words)


def generic_phrase_count(text: str) -> int:
    """Count of generic/template superlative phrases."""
    text_lower = text.lower()
    return sum(1 for phrase in GENERIC_SUPERLATIVES if phrase in text_lower)


def bot_disclaimer_count(text: str) -> int:
    """Count of phrases typical in incentivised/bot reviews."""
    text_lower = text.lower()
    return sum(1 for phrase in BOT_PHRASES if phrase in text_lower)


def sentiment_extremity(text: str) -> float:
    """
    Extremely positive OR extremely negative sentiment = suspicious.
    Returns 0 (neutral/normal) to 1 (extreme).
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1
    return abs(polarity)  # closer to 1 = extreme


def review_length_score(text: str) -> float:
    """
    Very short reviews (< 20 words) or suspiciously long (> 400 words) 
    both lose trust. Sweet spot: 30-150 words.
    Returns penalty 0-1 (1 = suspicious length).
    """
    words = len(text.split())
    if words < 15:
        return 0.9
    elif words < 30:
        return 0.4
    elif words <= 150:
        return 0.0
    elif words <= 300:
        return 0.1
    else:
        return 0.3


def specific_detail_score(text: str) -> float:
    """
    Genuine reviews mention specific product details, model numbers,
    use cases, comparisons. Returns 0 (no detail) to 1 (rich detail).
    """
    # Look for numbers, model refs, comparisons, specific features
    has_numbers = bool(re.search(r'\b\d+\b', text))
    has_comparison = any(w in text.lower() for w in [
        "compared to", "better than", "worse than", "unlike", "similar to",
        "previous", "old", "new version", "upgrade", "vs", "versus"
    ])
    has_use_case = any(w in text.lower() for w in [
        "i use", "using it for", "works for", "perfect for", "good for",
        "daily", "weekly", "months", "days", "weeks", "years"
    ])
    has_specific_feature = any(w in text.lower() for w in [
        "battery", "screen", "camera", "delivery", "packaging", "size",
        "color", "quality", "material", "smell", "sound", "fit",
        "price", "value", "customer service", "return", "refund"
    ])

    score = sum([has_numbers, has_comparison, has_use_case, has_specific_feature])
    return score / 4.0


def first_person_ratio(text: str) -> float:
    """Genuine reviews use first-person pronouns naturally."""
    words = word_tokenize(text.lower())
    first_person = ['i', 'my', 'me', 'myself', 'mine', 'we', 'our', 'us']
    fp_count = sum(1 for w in words if w in first_person)
    total = len([w for w in words if w.isalpha()])
    if total == 0:
        return 0.0
    ratio = fp_count / total
    # Too high (>0.25) or too low (<0.02) is suspicious
    if ratio < 0.02:
        return 0.7  # impersonal, possibly bot
    elif ratio > 0.3:
        return 0.5  # overly self-referential
    return 0.0


def punctuation_abuse(text: str) -> float:
    """Multiple consecutive punctuation = low quality / bot."""
    matches = re.findall(r'[!?]{2,}|\.{3,}', text)
    return min(len(matches) / 5.0, 1.0)


def detect_red_flags(text: str) -> list:
    """Return human-readable list of detected issues."""
    flags = []
    text_lower = text.lower()

    if caps_ratio(text) > 0.3:
        flags.append("Excessive use of CAPS (aggressive tone or bot-like)")

    if exclamation_density(text) > 2:
        flags.append("Too many exclamation marks per sentence")

    if repetition_score(text) > 0.15:
        flags.append("High word repetition detected (template-like content)")

    gc = generic_phrase_count(text)
    if gc >= 2:
        flags.append(f"Contains {gc} generic/template phrases (e.g. 'highly recommend', 'best ever')")

    if bot_disclaimer_count(text) > 0:
        flags.append("Contains incentivised review disclaimer language")

    if len(text.split()) < 15:
        flags.append("Review too short to be meaningful (< 15 words)")

    if specific_detail_score(text) < 0.25:
        flags.append("Lacks specific product details (generic opinion, no facts)")

    if punctuation_abuse(text) > 0.3:
        flags.append("Punctuation abuse detected (!! ??? ...)")

    if sentiment_extremity(text) > 0.85:
        flags.append("Extremely polarised sentiment (unusually strong emotion)")

    if not flags:
        flags.append("No major red flags detected")

    return flags


# ─── Core Scoring ─────────────────────────────────────────────────────────────

def compute_fake_probability(text: str) -> dict:
    """
    Compute weighted fake probability for a single review.
    Returns score 0-100 where 100 = definitely fake.
    """
    # Individual feature scores (all 0-1, higher = more fake)
    f_caps        = min(caps_ratio(text) / 0.4, 1.0)
    f_exclaim     = min(exclamation_density(text) / 3.0, 1.0)
    f_repetition  = min(repetition_score(text) / 0.2, 1.0)
    f_generic     = min(generic_phrase_count(text) / 3.0, 1.0)
    f_bot         = min(bot_disclaimer_count(text) / 2.0, 1.0) * 1.5  # heavy penalty
    f_length      = review_length_score(text)
    f_no_detail   = 1.0 - specific_detail_score(text)
    f_first_person = first_person_ratio(text)
    f_punct       = punctuation_abuse(text)
    f_sentiment   = max(0, sentiment_extremity(text) - 0.5) * 2  # only penalise extreme

    # Weighted sum
    weights = {
        'caps':         (f_caps,         0.08),
        'exclaim':      (f_exclaim,       0.08),
        'repetition':   (f_repetition,    0.12),
        'generic':      (f_generic,       0.15),
        'bot':          (f_bot,           0.15),
        'length':       (f_length,        0.10),
        'no_detail':    (f_no_detail,     0.15),
        'first_person': (f_first_person,  0.07),
        'punct':        (f_punct,         0.05),
        'sentiment':    (f_sentiment,     0.05),
    }

    weighted_score = sum(score * weight for score, weight in weights.values())
    fake_probability = round(min(weighted_score * 100, 100), 1)

    return {
        "fake_probability": fake_probability,
        "authenticity_score": round(100 - fake_probability, 1),
        "feature_breakdown": {k: round(v[0], 3) for k, v in weights.items()}
    }


def classify_review(authenticity_score: float) -> dict:
    """Map authenticity score to label + confidence."""
    if authenticity_score >= 75:
        return {"label": "GENUINE", "confidence": "HIGH", "emoji": "✅"}
    elif authenticity_score >= 55:
        return {"label": "LIKELY GENUINE", "confidence": "MEDIUM", "emoji": "🟡"}
    elif authenticity_score >= 35:
        return {"label": "SUSPICIOUS", "confidence": "MEDIUM", "emoji": "🟠"}
    else:
        return {"label": "LIKELY FAKE", "confidence": "HIGH", "emoji": "❌"}


# ─── Product-Level Trust Rating ───────────────────────────────────────────────

def compute_trust_rating(reviews_results: list) -> dict:
    """Aggregate per-review scores into an overall product trust rating."""
    if not reviews_results:
        return {"trust_rating": 0, "grade": "N/A", "summary": "No reviews to analyse"}

    scores = [r["authenticity_score"] for r in reviews_results]
    avg_score = sum(scores) / len(scores)

    fake_count = sum(1 for r in reviews_results if r["classification"]["label"] in ["LIKELY FAKE", "SUSPICIOUS"])
    fake_ratio = fake_count / len(reviews_results)

    # Penalise if high proportion of suspicious reviews
    penalty = fake_ratio * 20
    trust_score = round(max(avg_score - penalty, 0), 1)

    if trust_score >= 80:
        grade, summary = "A", "Highly trustworthy — reviews appear genuine"
    elif trust_score >= 65:
        grade, summary = "B", "Mostly trustworthy — minor concerns detected"
    elif trust_score >= 50:
        grade, summary = "C", "Moderate trust — several suspicious reviews present"
    elif trust_score >= 35:
        grade, summary = "D", "Low trust — significant fake review activity detected"
    else:
        grade, summary = "F", "Very low trust — majority of reviews appear fake"

    return {
        "trust_score": trust_score,
        "grade": grade,
        "summary": summary,
        "total_reviews_analysed": len(reviews_results),
        "flagged_as_suspicious": fake_count,
        "fake_ratio_percent": round(fake_ratio * 100, 1)
    }