from app.services.sync_service import SyncService

service = SyncService()

count = service.sync_premier_league()

service.close()

print(f"Synced {count} Premier League matches")