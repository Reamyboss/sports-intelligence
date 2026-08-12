import time

from app.services.sync_service import SyncService

# Same competition list as scripts/sync_all_competitions.py, confirmed
# available via GET /v4/competitions against the configured API key.
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

# Free tier is rate-limited (~10 requests/minute); one call per
# competition here, so this pacing has plenty of margin.
REQUEST_DELAY_SECONDS = 6.5


def main():
    sync_service = SyncService()

    for code in COMPETITIONS:
        try:
            count = sync_service.sync_teams(code)
            status = f"{count} teams"
        except Exception as exc:
            status = f"FAILED ({exc})"

        print(f"{code}: {status}", flush=True)

        time.sleep(REQUEST_DELAY_SECONDS)

    sync_service.close()

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
