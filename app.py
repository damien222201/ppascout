"""
PPAScout
--------
Crowdsourced reviews of NYSC Places of Primary Assignment (PPAs). The
federal NYSC allawee is fixed and uniform, but many PPAs pay an additional
monthly top-up that varies hugely — and corps members often have real
choice in where they end up, especially once they arrive in their state of
deployment. PPAScout collects real reviews (rating, top-up, accommodation,
notes) so incoming corps members can make an informed choice instead of
guessing or relying on rumor.

No official source publishes this data — self-reported by design, same
pattern as the rest of this project series.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from models import db, PPAReview
from reference_data import STATES, SECTORS, SERVICE_YEARS
from utils import is_valid_email, is_sane_topup, is_rate_limited, ppas_for_state, top_paying_states


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    database_url = os.environ.get("DATABASE_URL", "sqlite:///ppascout_dev.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        total_reviews = PPAReview.query.count()
        return render_template(
            "index.html", states=STATES, sectors=SECTORS, service_years=SERVICE_YEARS,
            total_reviews=total_reviews,
        )

    @app.route("/review", methods=["POST"])
    def review():
        email = request.form.get("email", "").strip()
        state = request.form.get("state", "").strip()
        ppa_name = request.form.get("ppa_name", "").strip()
        sector = request.form.get("sector", "").strip()
        service_year = request.form.get("service_year", "").strip()
        monthly_topup = request.form.get("monthly_topup", "").strip()
        accommodation_provided = request.form.get("accommodation_provided") == "yes"
        rating = request.form.get("rating", "").strip()
        review_text = request.form.get("review_text", "").strip() or None
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("index"))
        if state not in STATES:
            flash("Please select a valid state.", "error")
            return redirect(url_for("index"))
        if not ppa_name or len(ppa_name) > 200:
            flash("Please enter the PPA name.", "error")
            return redirect(url_for("index"))
        if sector not in SECTORS:
            flash("Please select a valid sector.", "error")
            return redirect(url_for("index"))
        if service_year not in SERVICE_YEARS:
            flash("Please select a valid service year.", "error")
            return redirect(url_for("index"))
        if monthly_topup and not is_sane_topup(monthly_topup):
            flash("Please enter a realistic monthly top-up amount, or leave it blank.", "error")
            return redirect(url_for("index"))
        if rating not in ("1", "2", "3", "4", "5"):
            flash("Please select a rating from 1 to 5.", "error")
            return redirect(url_for("index"))
        if is_rate_limited(email, ip_address):
            flash("You've submitted a few reviews recently — please wait a bit before submitting again.", "error")
            return redirect(url_for("index"))

        new_review = PPAReview(
            email=email, state=state, ppa_name=ppa_name, sector=sector,
            service_year=service_year,
            monthly_topup=float(monthly_topup) if monthly_topup else None,
            accommodation_provided=accommodation_provided,
            rating=int(rating), review=review_text, ip_address=ip_address,
        )
        db.session.add(new_review)
        db.session.commit()

        flash("Thanks — your PPA review has been added.", "success")
        return redirect(url_for("index"))

    @app.route("/browse")
    def browse():
        state = request.args.get("state", "").strip()
        sector = request.args.get("sector", "").strip()
        if sector and sector not in SECTORS:
            sector = ""

        results = ppas_for_state(state, sector or None) if state in STATES else []
        return render_template(
            "browse.html", states=STATES, sectors=SECTORS,
            state=state, sector=sector, results=results,
        )

    @app.route("/stats")
    def stats():
        sector = request.args.get("sector", "").strip()
        if sector and sector not in SECTORS:
            sector = ""
        top_states = top_paying_states(sector or None)
        total_reviews = PPAReview.query.count()
        return render_template(
            "stats.html", sectors=SECTORS, sector=sector,
            top_states=top_states, total_reviews=total_reviews,
        )

    @app.route("/api/reviews")
    def api_reviews():
        state = request.args.get("state", "").strip()
        query = PPAReview.query
        if state in STATES:
            query = query.filter_by(state=state)
        reviews = query.order_by(PPAReview.created_at.desc()).limit(200).all()
        return jsonify([r.to_dict() for r in reviews])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
