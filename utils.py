"""Shared helpers: email validation, rate limiting, PPA rollups."""
import re
import statistics
from datetime import datetime, timedelta
from models import db, PPAReview

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

RATE_LIMIT_WINDOW_MINUTES = 60
RATE_LIMIT_MAX_REPORTS = 5

MAX_SANE_TOPUP = 500_000  # NGN/month — reject obvious typos above this


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_sane_topup(amount):
    if amount in (None, ""):
        return True  # top-up is optional — some PPAs pay nothing extra
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False
    return 0 <= amount <= MAX_SANE_TOPUP


def is_rate_limited(email, ip_address):
    window_start = datetime.utcnow() - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
    count = PPAReview.query.filter(
        PPAReview.created_at >= window_start,
        db.or_(PPAReview.email == email, PPAReview.ip_address == ip_address),
    ).count()
    return count >= RATE_LIMIT_MAX_REPORTS


def ppas_for_state(state, sector=None):
    """All PPAs reviewed in a state, grouped with aggregate stats, best-rated first."""
    query = PPAReview.query.filter_by(state=state)
    if sector:
        query = query.filter_by(sector=sector)
    reviews = query.all()

    grouped = {}
    for r in reviews:
        key = r.ppa_name.strip()
        grouped.setdefault(key, []).append(r)

    results = []
    for ppa_name, items in grouped.items():
        ratings = [i.rating for i in items]
        topups = [float(i.monthly_topup) for i in items if i.monthly_topup is not None]
        results.append({
            "ppa_name": ppa_name,
            "sector": items[0].sector,
            "review_count": len(items),
            "avg_rating": statistics.mean(ratings),
            "avg_topup": statistics.mean(topups) if topups else None,
            "any_accommodation": any(i.accommodation_provided for i in items),
            "latest_review": max(items, key=lambda i: i.created_at),
        })
    results.sort(key=lambda x: x["avg_rating"], reverse=True)
    return results


def top_paying_states(sector=None, limit=10):
    """States with the highest average reported top-up, for a cross-state view."""
    query = PPAReview.query.filter(PPAReview.monthly_topup.isnot(None))
    if sector:
        query = query.filter_by(sector=sector)
    reviews = query.all()

    by_state = {}
    for r in reviews:
        by_state.setdefault(r.state, []).append(float(r.monthly_topup))

    results = [
        {"state": state, "avg_topup": statistics.mean(vals), "review_count": len(vals)}
        for state, vals in by_state.items()
    ]
    results.sort(key=lambda x: x["avg_topup"], reverse=True)
    return results[:limit]
