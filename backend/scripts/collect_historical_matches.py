from app.collectors.historical_match_collector import HistoricalMatchCollector


def main():
    collector = HistoricalMatchCollector()

    total = collector.collect(
        competition="PL",
        season=2025,
    )

    print(f"Collected {total} historical matches.")


if __name__ == "__main__":
    main()