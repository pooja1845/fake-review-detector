"""
Flipkart Fake Review Detector API
----------------------------------
Endpoints:
  POST /analyze/review      → Analyse a single review
  POST /analyze/product     → Analyse multiple reviews for a product
  GET  /health              → Health check
  GET  /docs                → Auto Swagger UI (FastAPI built-in)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from detector import (
    compute_fake_probability,
    classify_review,
    detect_red_flags,
    compute_trust_rating
)

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Flipkart Fake Review Detector API",
    description="""
## 🛒 Fake Review Detection for E-Commerce

Detect fake, bot-generated, or incentivised reviews using NLP + heuristic analysis.

### Features
- **Single review analysis** with authenticity score (0–100)
- **Bulk product analysis** with overall trust rating
- **Red flag detection** — specific reasons why a review is suspicious
- **Feature breakdown** — transparency into what the model checks

### Built for Flipkart Grid 8.0 — Software Track
""",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ────────────────────────────────────────────────

class SingleReviewRequest(BaseModel):
    review_text: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        example="This product is absolutely amazing!! Best purchase EVER!! Highly recommend to everyone!!!",
        description="The review text to analyse"
    )
    reviewer_name: Optional[str] = Field(None, example="John D.")
    rating: Optional[float] = Field(None, ge=1, le=5, example=5.0)


class ProductReviewsRequest(BaseModel):
    product_name: Optional[str] = Field(None, example="Noise Smartwatch Pro X")
    product_id: Optional[str] = Field(None, example="PROD_12345")
    reviews: List[SingleReviewRequest] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of reviews to analyse (max 50)"
    )


class ReviewAnalysisResult(BaseModel):
    review_text: str
    reviewer_name: Optional[str]
    rating: Optional[float]
    authenticity_score: float
    fake_probability: float
    classification: dict
    red_flags: List[str]
    feature_breakdown: dict
    analysed_at: str


class ProductAnalysisResult(BaseModel):
    product_name: Optional[str]
    product_id: Optional[str]
    trust_rating: dict
    individual_reviews: List[dict]
    analysed_at: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Check if the API is running."""
    return {
        "status": "healthy",
        "service": "Flipkart Fake Review Detector",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/analyze/review", response_model=ReviewAnalysisResult, tags=["Analysis"])
def analyze_single_review(request: SingleReviewRequest):
    """
    ## Analyse a Single Review

    Returns:
    - **authenticity_score**: 0–100 (higher = more genuine)
    - **fake_probability**: 0–100 (higher = more likely fake)
    - **classification**: GENUINE / LIKELY GENUINE / SUSPICIOUS / LIKELY FAKE
    - **red_flags**: Specific reasons why the review is flagged
    - **feature_breakdown**: Transparency into what each NLP feature scored
    """
    try:
        text = request.review_text.strip()

        # Run detection
        scores = compute_fake_probability(text)
        classification = classify_review(scores["authenticity_score"])
        red_flags = detect_red_flags(text)

        # If rating is extreme (1 or 5) + review is suspicious, nudge score
        if request.rating in [1.0, 5.0]:
            scores["fake_probability"] = min(scores["fake_probability"] * 1.05, 100)
            scores["authenticity_score"] = max(100 - scores["fake_probability"], 0)
            classification = classify_review(scores["authenticity_score"])

        return ReviewAnalysisResult(
            review_text=text,
            reviewer_name=request.reviewer_name,
            rating=request.rating,
            authenticity_score=scores["authenticity_score"],
            fake_probability=scores["fake_probability"],
            classification=classification,
            red_flags=red_flags,
            feature_breakdown=scores["feature_breakdown"],
            analysed_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/product", response_model=ProductAnalysisResult, tags=["Analysis"])
def analyze_product_reviews(request: ProductReviewsRequest):
    """
    ## Analyse All Reviews for a Product

    Submit multiple reviews for a single product and get:
    - **Per-review** analysis (score, classification, red flags)
    - **Overall trust rating** (A–F grade with summary)
    - **Aggregate stats** (% fake, total flagged, etc.)
    """
    try:
        results = []

        for rev in request.reviews:
            text = rev.review_text.strip()
            scores = compute_fake_probability(text)
            classification = classify_review(scores["authenticity_score"])
            red_flags = detect_red_flags(text)

            if rev.rating in [1.0, 5.0]:
                scores["fake_probability"] = min(scores["fake_probability"] * 1.05, 100)
                scores["authenticity_score"] = max(100 - scores["fake_probability"], 0)
                classification = classify_review(scores["authenticity_score"])

            results.append({
                "review_text": text[:200] + "..." if len(text) > 200 else text,
                "reviewer_name": rev.reviewer_name,
                "rating": rev.rating,
                "authenticity_score": scores["authenticity_score"],
                "fake_probability": scores["fake_probability"],
                "classification": classification,
                "red_flags": red_flags,
                "feature_breakdown": scores["feature_breakdown"]
            })

        trust_rating = compute_trust_rating(results)

        return ProductAnalysisResult(
            product_name=request.product_name,
            product_id=request.product_id,
            trust_rating=trust_rating,
            individual_reviews=results,
            analysed_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Flipkart Fake Review Detector API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "analyze_review": "POST /analyze/review",
            "analyze_product": "POST /analyze/product"
        }
    }