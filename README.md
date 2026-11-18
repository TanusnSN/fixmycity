# FixMyCity - Public Infrastructure Complaint and Tracking System

Citizens report road, streetlight, water and drainage problems with a map pin and photos,
and track progress. Administrators verify, categorise, assign to departments, prioritise
and resolve them. A duplicate-detection engine links repeat reports of the same problem.

**Stack:** FastAPI, SQLModel, SQLite/PostgreSQL, JWT auth, HTML/CSS/JS + Leaflet (OpenStreetMap),
Docker, GitHub Actions.

## Run locally
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.create_admin      # admin + departments
python -m app.seed              # optional demo data
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 (app) and http://127.0.0.1:8000/docs (API docs).

| Role | Login |
|---|---|
| Admin | admin@fixmycity.local / admin123 |
| Citizen (after seed) | citizen@fixmycity.local / citizen123 |

These are local demo credentials only. Set `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` for real deployments.

## Tests
```
pytest -v
```

## Docker
```
docker build -t fixmycity .
docker run -p 8000:8000 fixmycity

docker compose up --build       # app + PostgreSQL
docker compose exec web python -m app.create_admin
docker compose exec web python -m app.seed
```

## How the innovative features work
**Duplicate detection** (`app/services/duplicate.py`): same category, within 100 m, then
`confidence = 0.6 x proximity + 0.4 x text similarity`. 75%+ = likely duplicate, 50-75% = possible.
Citizens see matches while filing and can support the existing complaint instead; admins can merge
duplicates under one main complaint, which then carries their status.

**Priority scoring** (`app/services/priority.py`): category base + 4 per duplicate + 2 per supporter
+ 1.5 per day open + 15 near a school/hospital/etc. Admins see the exact breakdown and can override it.

## Project layout
```
app/
  main.py  config.py  database.py  models.py  schemas.py  auth.py
  create_admin.py  seed.py
  routers/   auth.py  complaints.py  admin.py
  services/  duplicate.py  priority.py
  static/    index.html  style.css  app.js
tests/
Dockerfile  docker-compose.yml  .github/workflows/ci.yml
```
