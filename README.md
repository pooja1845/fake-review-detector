# 🛒 Flipkart Fake Review Detector API

A production-ready REST API that detects fake, bot-generated, and incentivised product reviews using NLP + heuristic scoring — built as a solution to a real Flipkart business problem.

---
##  Open Swagger UI
Visit :  http://localhost:8000/docs

## 🎯 Problem Statement

Fake reviews cost e-commerce platforms billions in lost consumer trust annually. Flipkart (and platforms like it) need scalable, automated ways to flag suspicious reviews before they influence buying decisions.

This API provides:
- Per-review **authenticity score** (0–100)
- **Fake/Genuine classification** with confidence level
- **Specific red flag reasons** (not just a score — WHY it's flagged)
- **Product-level trust rating** (A–F grade) across all reviews

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/pooja1845/fake-review-detector.git
cd fake-review-detector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API server
uvicorn main:app --reload

# 4. Open Swagger UI
# Visit http://localhost:8000/docs
```

---

## 📡 API Endpoints

### `POST /analyze/review` — Single Review Analysis

**Request:**
```json
{
  "review_text": "BEST PRODUCT EVER!! Highly recommend to EVERYONE!! Must buy!!",
  "reviewer_name": "John D.",
  "rating": 5
}
```

**Response:**
```json
{
  "authenticity_score": 33.5,
  "fake_probability": 66.5,
  "classification": {
    "label": "LIKELY FAKE",
    "confidence": "HIGH",
    "emoji": "❌"
  },
  "red_flags": [
    "Excessive use of CAPS (aggressive tone or bot-like)",
    "Contains 3 generic/template phrases (e.g. 'highly recommend', 'best ever')",
    "Punctuation abuse detected (!! ??? ...)"
  ],
  "feature_breakdown": {
    "caps": 0.812,
    "exclaim": 0.667,
    "repetition": 0.0,
    "generic": 1.0,
    "bot": 0.0,
    "length": 0.9,
    "no_detail": 0.75,
    "first_person": 0.0,
    "punct": 0.6,
    "sentiment": 0.7
  }
}
```

---

### `POST /analyze/product` — Bulk Product Analysis

**Request:**
```json
{
  "product_name": "Noise Smartwatch Pro X",
  "product_id": "PROD_12345",
  "reviews": [
    { "review_text": "BEST EVER!! Love it!!", "rating": 5 },
    { "review_text": "Battery lasts 6-7 hours. Compared to my previous watch, sound quality is better. Good value.", "rating": 4 }
  ]
}
```

**Response includes:**
```json
{
  "trust_rating": {
    "trust_score": 51.6,
    "grade": "C",
    "summary": "Moderate trust — several suspicious reviews present",
    "total_reviews_analysed": 6,
    "flagged_as_suspicious": 3,
    "fake_ratio_percent": 50.0
  },
  "individual_reviews": [ ... ]
}
```

---

## 🧠 How It Works

The detector extracts **10 NLP features** from each review and combines them with a weighted scoring model:

| Feature | What it detects | Weight |
|--------|----------------|--------|
| CAPS ratio | Shouting/aggressive bot tone | 8% |
| Exclamation density | Emotional manipulation | 8% |
| Word repetition | Template/copy-paste content | 12% |
| Generic phrases | "Best ever", "highly recommend" | 15% |
| Bot disclaimers | "Received free in exchange for review" | 15% |
| Review length | Too short or suspiciously long | 10% |
| Specific details | Mentions features, use case, comparisons | 15% |
| First-person ratio | Impersonal = likely bot | 7% |
| Punctuation abuse | `!!!`, `???`, `...` overuse | 5% |
| Sentiment extremity | Unnaturally polar reviews | 5% |

**Classification thresholds:**
- ✅ **GENUINE** — Score ≥ 75
- 🟡 **LIKELY GENUINE** — Score 55–74
- 🟠 **SUSPICIOUS** — Score 35–54
- ❌ **LIKELY FAKE** — Score < 35

---

## 🛠 Tech Stack

- **FastAPI** — REST API framework
- **TextBlob** — Sentiment analysis
- **NLTK** — Tokenisation, stopword removal
- **Pydantic** — Request/response validation
- **Uvicorn** — ASGI server

---

## 🔬 Test Results (Sample)

```
Review: "BEST PRODUCT EVER!!! Absolutely amazing!! Highly recommend to EVERYONE!!"
→ ❌ LIKELY FAKE (Score: 33.5) | Flags: CAPS abuse, generic phrases, punctuation abuse

Review: "I received this product for free in exchange for an honest review."
→ 🟠 SUSPICIOUS (Score: 43.6) | Flags: Incentivised review language

Review: "Battery lasts 6-7 hours. Compared to previous model, sound is better. Good value."
→ ✅ GENUINE (Score: 97.4) | No red flags
```

---

## 🗂 Project Structure

```
fake-review-detector/
├── main.py           # FastAPI app — all endpoints
├── detector.py       # NLP engine — feature extraction + scoring
├── test_api.py       # Standalone tests (no server needed)
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## 📈 Business Impact

- Scalable to millions of reviews/day with async processing
- Explainable outputs — not a black box, every decision is justified
- Can be integrated into Flipkart's review pipeline pre-publish
- Reduces fake review influence on product rankings and buyer decisions

---

