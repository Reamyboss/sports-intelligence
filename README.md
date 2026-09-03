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
python sync_matches.py                          # Premier League fixtures only
python scripts/collect_historical_matches.py     # Premier League 2025/26 results only
python scripts/sync_all_competitions.py          # all 12 available competitions, paced for rate limits (~3-4 min)
python scripts/sync_all_teams.py                 # team rosters for all 12 competitions (~1-2 min)
python scripts/backfill_source_field.py          # one-time: tags existing rows source=football-data.org
python scripts/collect_football_data_co_uk.py    # 10 extra seasons of free historical depth, 8 competitions
python scripts/audit_data_provenance.py          # row counts by source/competition, for a sanity check
```

These write to `app/data/matches.json` (current-season fixtures),
`app/data/historical_matches.json` (completed results, used for team form/
goals/streak evidence), and `app/data/teams.json` (team directory). All
saves merge by id — re-running any of these is safe and won't erase other
competitions' data.

`collect_football_data_co_uk.py` pulls free, public, no-API-key historical
results from [football-data.co.uk](https://www.football-data.co.uk) — 10
seasons (2015/16–2024/25) across the 8 competitions it covers (Premier
League, Championship, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie,
Primeira Liga; Champions League and Brasileirão aren't in its dataset).
Every row is tagged `source: "football-data.co.uk"` so it's always
distinguishable from live football-data.org data, deduplicated against it by
`(competition, date, home team, away team)` — football-data.org's own data
always wins a collision — and only ever saved for a team whose
football-data.co.uk short name (`"Man United"`) has a verified, hand-checked
mapping to this platform's real full name (`"Manchester United FC"`) in
`app/data/football_data_co_uk_team_map.json`. A club with no entry there is
skipped and logged, never guessed — re-run `scripts/seed_team_name_map.py`
after syncing more teams to see what can now be added.

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

- **A team's `league` field reflects whichever competition it was most
  recently synced under, not all of them.** `Team.league` is a single
  string, but a club can appear in several competitions (e.g. a domestic
  league and the Champions League) with the same football-data.org id — the
  last sync wins. Visible in the real data: Champions League overlap pulls
  some clubs' `league` away from their domestic league. Fixing this properly
  means changing `league: str` to a list, which hasn't been done since it
  changes the API contract.
- **Most `manager` values are `"Unknown"`.** football-data.org's coach data
  is sparse on the current plan — this isn't a bug in the sync, the upstream
  field is genuinely null for most teams right now.
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
