# PPAScout

A community-reviewed guide to NYSC Places of Primary Assignment (PPAs). The federal NYSC allawee is fixed and uniform nationwide, but many PPAs pay an additional monthly top-up that varies enormously — and corps members often have real choice in where they're placed, especially once they arrive in their state of deployment. PPAScout collects honest reviews so incoming corps members can choose with actual information instead of rumor.

## Why

Every service year, corps members arrive in their state and scramble to find a good PPA based on word of mouth, Facebook groups, and luck. PPAScout tries to turn that into something searchable: real ratings, real top-up figures, real notes on what it's actually like.

## Features

- **Review a PPA** — state, PPA name, sector, service year, monthly top-up (optional — some PPAs pay nothing extra), whether accommodation is provided, a 1–5 star rating, and an optional written review. Email required (never shown) to cut spam, with rate limiting (5 reviews/hour per email or IP).
- **Browse by state** — PPAs reviewed in a state, best-rated first, with average top-up, review count, and the latest written review shown.
- **Top-paying states** — ranks states by average reported top-up, optionally filtered by sector.
- **JSON API** (`/api/reviews`) — recent reviews, optionally filtered by state.

## Tech stack

Same as the rest of this project series: Flask + Flask-SQLAlchemy, PostgreSQL on Render, server-rendered Jinja2, no JS framework.

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
export $(cat .env | xargs)

python app.py
```

Falls back to local SQLite (`ppascout_dev.db`) if `DATABASE_URL` isn't set. Visit `http://localhost:5000`.

## Deploying to Render

**Option A — blueprint:** push to GitHub, "New Blueprint" in Render pointed at the repo — `render.yaml` sets up the web service and free Postgres together.

**Option B — manual:** create a Postgres DB, create a Web Service (`pip install -r requirements.txt` / `gunicorn app:app`), add `DATABASE_URL` and `SECRET_KEY` env vars.

## Project structure

```
app.py              # routes + app factory
models.py           # PPAReview model
reference_data.py   # states, sectors, service years
utils.py            # validation, rate limiting, PPA/state aggregation
templates/           # index, browse, stats pages + shared base layout
static/style.css     # all styling
```

## Known limitations / next steps

- **PPA name matching is free text** — "Government Secondary School, Karu" and "GSS Karu" are treated as different entries right now. Fine for a first version; normalization/fuzzy matching would make aggregation more accurate over time.
- **No redeployment/request-process info** — reviews cover what a PPA is like, not how corps members got placed there (local government quota, direct request, etc.). Could be a useful future field.
- **No email verification**, same tradeoff as the rest of the series.
- **No way to flag/report a review** — if abuse becomes an issue, that's the natural next feature.

## License

MIT — see [LICENSE](LICENSE).
