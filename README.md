# Sports Intelligence Platform

An AI-powered sports decision intelligence backend. It doesn't just predict a
winner — it builds an explainable case: what supports each side, what's
uncertain, and why the system is or isn't confident.

Current scope: football (soccer), backed by real data from
[football-data.org](https://www.football-data.org/), across 12 competitions
including the Premier League, La Liga, Bundesliga, Serie A, Ligue 1, and the
Champions League.

## Architecture

```
Match Data (football-data.org)
    ↓
Match Repository / Service      app/repositories, app/services/match_service.py
    ↓
Knowledge Builder                app/knowledge/
    ↓
Match Profile
    ↓
Evidence Builder                 app/evidence/
    ↓
Reasoning Engine                 app/reasoning/
    ↓
Confidence Engine                app/confidence/
    ↓
Prediction Engine                app/prediction/
    ↓
Prediction API                   app/api/predictions.py
    ↓
Swagger / OpenAPI
```

Each layer has one job and doesn't reach into the others:

| Layer | Answers | Does not |
|---|---|---|
| Knowledge | What do we know about this match? | Predict anything |
| Evidence | What supports each outcome? | Draw conclusions |
| Reasoning | What conclusions follow from the evidence? | Assign a win probability |
| Confidence | How certain is the system? | Decide the outcome |
| Prediction | Orchestrates the above into one result | Contain evidence/reasoning logic itself |

## Setup

```bash
cd backend
python -m venv .venv          # if not already created
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```
FOOTBALL_DATA_API_KEY=your_football_data_org_key
```

A free key from football-data.org covers 12 competitions at roughly 10
requests/minute — see `scripts/sync_all_competitions.py` for the exact list
and pacing.

## Running the server

Must be run with `backend/` as the import root, not the repo root — running
from the wrong directory is the source of the classic
`ModuleNotFoundError: No module named 'app'`.

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for Swagger.

## Running tests

```bash
cd backend
pytest -v
```

`pytest.ini` sets `pythonpath = .`, so this works regardless of how pytest
itself is invoked. The suite (`tests/`) covers the reasoning/prediction/
confidence rules directly, regression-guards the two data-layer bugs
described below, runs the full pipeline against real synced data, and hits
every API route including 404 paths. It does **not** cover
`FootballDataProvider` / `SyncService` / `HistoricalMatchCollector` — those
make real network calls and would need HTTP mocking, which hasn't been added
yet.

## Getting real data

```bash
cd backend
python sync_matches.py                        # Premier League fixtures only
python scripts/collect_historical_matches.py   # Premier League 2025/26 results only
python scripts/sync_all_competitions.py        # all 12 available competitions, paced for rate limits (~3-4 min)
```

These write to `app/data/matches.json` (current-season fixtures) and
`app/data/historical_matches.json` (completed results, used for team form/
goals/streak evidence). Saves merge by match id — re-running any of these is
safe and won't erase other competitions' data.

## API surface

| Endpoint | Purpose |
|---|---|
| `GET /` | Health check |
| `GET /matches/` | List all matches |
| `GET /matches/{id}` | One match, 404 if unknown |
| `GET /teams/` | List teams |
| `GET /knowledge/{match_id}` | The match profile (facts only, no prediction) |
| `GET /prediction/{match_id}` | Full prediction: winner, probability, confidence, evidence-backed explanation |

CORS is open to `localhost:3000`/`5173` (both `localhost` and `127.0.0.1`) by
default for local frontend development — see `CORS_ORIGINS` in
`app/config.py`.

## Known limitations

- **`teams.json` has 2 hand-seeded teams.** No real team-sync exists yet;
  `/teams/` is nowhere near full coverage for any league.
- **No scheduled refresh.** Someone has to re-run the sync scripts manually
  to pick up new results as matches get played.
- **Reasoning rules are coarse binary thresholds**, not weighted (e.g. "away
  form ≥ 3 wins" as the only risk signal). Close matchups correctly produce
  no signal rather than a wrong one, but there's real room to make evidence
  more graded.
- **Two separate settings systems** — `app/config.py` (general app settings)
  and `app/core/settings.py` (football-data.org key only). Not yet unified;
  see the code comments / project history for why a naive merge is risky.
- **`matches.json` stores competition as a full name** ("Premier League")
  while `historical_matches.json` stores the short code ("PL") — same field,
  different convention between the two write paths. Doesn't break anything
  today since nothing filters across files by competition yet.
