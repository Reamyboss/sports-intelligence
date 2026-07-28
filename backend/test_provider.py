from app.providers.football_data_provider import FootballDataProvider

provider = FootballDataProvider()

matches = provider.fetch_matches()

print(f"Downloaded {len(matches)} matches")

provider.close()