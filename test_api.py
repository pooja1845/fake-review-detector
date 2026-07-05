"""
Quick test — runs without a server, directly calls detector logic.
Run: python3 test_api.py
"""

from detector import compute_fake_probability, classify_review, detect_red_flags, compute_trust_rating

FAKE_REVIEWS = [
    "BEST PRODUCT EVER!!! Absolutely amazing!! Highly recommend to EVERYONE!! 5 stars!! Must buy!!",
    "I received this product for free in exchange for an honest review. It is perfect. No complaints.",
    "Good",
    "love love love this!!! game changer life changing best purchase 100% worth every penny!!!!!",
]

GENUINE_REVIEWS = [
    "I've been using this for about 3 months daily. Battery lasts around 6-7 hours which is decent for the price. "
    "Compared to my previous model, the sound quality is noticeably better. The build feels a bit plastic but "
    "nothing that bothers me. Would say it's good value for money if you're not an audiophile.",

    "Delivery was quick (2 days). Packaging was intact. The product size is smaller than expected — "
    "I wish the listing mentioned dimensions. Works exactly as described. Customer service responded "
    "within hours when I had a query. Will probably buy again.",
]

MIXED = FAKE_REVIEWS + GENUINE_REVIEWS

print("=" * 60)
print("FAKE REVIEW DETECTOR — TEST RUN")
print("=" * 60)

for i, review in enumerate(MIXED, 1):
    result = compute_fake_probability(review)
    classification = classify_review(result["authenticity_score"])
    flags = detect_red_flags(review)

    print(f"\n[Review {i}]")
    print(f"  Text     : {review[:80]}...")
    print(f"  Auth Score: {result['authenticity_score']} / 100")
    print(f"  Label    : {classification['emoji']} {classification['label']} ({classification['confidence']})")
    print(f"  Red Flags:")
    for f in flags:
        print(f"    → {f}")

# Product-level trust rating
all_results = []
for review in MIXED:
    r = compute_fake_probability(review)
    c = classify_review(r["authenticity_score"])
    all_results.append({"authenticity_score": r["authenticity_score"], "classification": c})

trust = compute_trust_rating(all_results)
print("\n" + "=" * 60)
print("PRODUCT TRUST RATING")
print("=" * 60)
print(f"  Trust Score : {trust['trust_score']} / 100")
print(f"  Grade       : {trust['grade']}")
print(f"  Summary     : {trust['summary']}")
print(f"  Flagged     : {trust['flagged_as_suspicious']} / {trust['total_reviews_analysed']} reviews")
print(f"  Fake Ratio  : {trust['fake_ratio_percent']}%")