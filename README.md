# 🛒 Flipkart Fake Review Detector

An interactive web application and API that evaluates the authenticity of e-commerce reviews using Natural Language Processing (NLP) and content heuristics. Developed for the **Flipkart Grid 8.0 — Software Track**.

---

## 🌟 Features

- **Single Review Analyzer**: Evaluate individual reviews for red flags (ALL-CAPS, punctuation abuse, bot disclaimer language, generic promotional phrasing, etc.) and calculate a weighted authenticity score (0-100%).
- **Bulk Product-Level Trust Rating**: Submit multiple reviews for a product to calculate an overall trust grade (A to F) and trust score.
- **Pattern Diagnostics Breakdown**: A beautiful horizontal bar visualization showing exact score breakdown across all heuristic criteria (e.g. capitalized text ratio, exclamation rates, word repetition, sponsor disclaimer checks).
- **Glassmorphic Interactive UI**: A dark-mode single-page frontend served directly from the FastAPI root `/` endpoint.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **NLP / Text Analysis**: [NLTK](https://www.nltk.org/), [TextBlob](https://textblob.readthedocs.io/)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism styling), Vanilla JavaScript

---

## 🚀 Setup & Installation

### 1. Install Dependencies
Ensure you have Python installed, then install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Uvicorn local server. Using the `-X utf8` flag ensures Unicode support for emoji renderings on all platforms:
```bash
python -X utf8 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open in Browser
Visit the following URLs:
- **Interactive UI Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📂 Project Structure

- `detector.py`: Core logic for NLP pattern evaluations, heuristic scoring weights, and rating nudge calculators.
- `main.py`: FastAPI server setting up analysis routes (`/analyze/review`, `/analyze/product`) and rendering the HTML/CSS/JS frontend dashboard.
- `test_api.py`: Offline script to verify scoring accuracy against sample genuine/fake reviews.
- `requirements.txt`: Python package requirements.
