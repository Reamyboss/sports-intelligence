import time

from app.collectors.historical_match_collector import HistoricalMatchCollector
from app.services.sync_service import SyncService

# Every competition available on the current football-data.org plan
# (confirmed via GET /v4/competitions against the configured API key).
COMPETITIONS = [
    "PL",   # Premier League - England
    "ELC",  # Championship - England
    "PD",   # Primera Division - Spain
    "BL1",  # Bundesliga - Germany
    "SA",   # Serie A - Italy
    "FL1",  # Ligue 1 - France
    "DED",  # Eredivisie - Netherlands
    "PPL",  # Primeira Liga - Portugal
    "CL",   # UEFA Champions League
    "BSA",  # Campeonato Brasileiro Serie A - Brazil
    "WC",   # FIFA World Cup
    "EC",   # UEFA European Championship
]

HISTORICAL_SEASON = 2025

# Free tier is rate-limited (~10 requests/minute). Two calls per
# competition (fixtures + historical), so this stays safely under that.
REQUEST_DELAY_SECONDS = 6.5


def main():
    sync_service = SyncService()
    collector = HistoricalMatchCollector()

    summary = []

    for code in COMPETITIONS:
        try:
            fixture_count = sync_service.sync_competition(code)
            fixture_status = f"{fixture_count} current fixtures"
        except Exception as exc:
            fixture_status = f"fixtures FAILED ({exc})"

        time.sleep(REQUEST_DELAY_SECONDS)

        try:
            historical_count = collector.collect(
                competition=code,
                season=HISTORICAL_SEASON,
            )
            historical_status = f"{historical_count} historical matches"
        except Exception as exc:
            historical_status = f"historical FAILED ({exc})"

        time.sleep(REQUEST_DELAY_SECONDS)

        line = f"{code}: {fixture_status}, {historical_status}"
        print(line, flush=True)
        summary.append(line)

    sync_service.close()
    collector.close()

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
