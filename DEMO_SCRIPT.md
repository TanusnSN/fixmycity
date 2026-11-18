# Expo demo script (about 6 minutes)

0. **Before you start:** `python -m app.seed`, start the app, keep Docker Desktop and the GitHub Actions tab open.

1. **DevOps (1 min)**
   - GitHub repo: branches `main` / `dev` / feature branches, merged pull requests.
   - Actions tab: a green run (tests, then Docker build).
   - Terminal: `docker build -t fixmycity .`, `docker run -p 8000:8000 fixmycity`, `docker ps`.

2. **Citizen flow (2 min)**
   - Log in as citizen@fixmycity.local. Report a pothole near the bus stop (drop a pin close to the seeded one).
   - Point out the live "similar complaints nearby" warning with the match percentage. Click "I also face this".
   - Open "My complaints" and show the status timeline.

3. **Admin flow (2 min)**
   - Log in as admin@fixmycity.local. Dashboard: totals, overdue, charts.
   - Open a complaint: "Why this priority?" breakdown, possible duplicates, merge one.
   - Move the status Verified -> Assigned (department) -> In progress -> Resolved with remarks.
   - Log back in as the citizen: the timeline updated, and the citizen can reopen it.

4. **Innovation + engineering (1 min)**
   - Duplicate detection formula (distance + text) and transparent priority score.
   - Role-based access, validated photo uploads, audit log, automated tests (`pytest -v`).

## Likely examiner questions
- *Why FastAPI?* Fast to build, automatic API docs, type-checked requests.
- *How do you stop a citizen using admin features?* Every admin route depends on `require_admin`, checked against the database role.
- *How are duplicates found?* Same category + Haversine distance under 100 m + text similarity, combined into a confidence score.
- *What happens when a duplicate is merged?* It follows the main complaint's status, so every reporter sees progress.
- *What would you improve?* Email/SMS notifications, image-based duplicate detection, a mobile app, Azure Blob Storage for photos.
