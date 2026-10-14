"""Database model for PPAScout."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PPAReview(db.Model):
    __tablename__ = "ppa_reviews"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    state = db.Column(db.String(50), nullable=False, index=True)
    ppa_name = db.Column(db.String(200), nullable=False, index=True)
    sector = db.Column(db.String(30), nullable=False, index=True)
    service_year = db.Column(db.String(9), nullable=False)  # e.g. "2025/2026" batch
    monthly_topup = db.Column(db.Numeric(10, 2), nullable=True)  # on top of federal allawee; nullable since some PPAs pay none
    accommodation_provided = db.Column(db.Boolean, nullable=False, default=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def ppa_key(self):
        return f"{self.state}|{self.ppa_name.strip().lower()}"

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "ppa_name": self.ppa_name,
            "sector": self.sector,
            "service_year": self.service_year,
            "monthly_topup": float(self.monthly_topup) if self.monthly_topup is not None else None,
            "accommodation_provided": self.accommodation_provided,
            "rating": self.rating,
            "review": self.review,
            "created_at": self.created_at.isoformat() + "Z",
        }
