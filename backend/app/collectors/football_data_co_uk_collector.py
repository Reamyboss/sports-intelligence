from dataclasses import dataclass, field

from app.collectors.football_data_co_uk_normalizer import (
    COMPETITION_CODE_MAP,
    normalize_row,
    parse_csv_rows,
)
from app.providers.football_data_co_uk_provider import FootballDataCoUkProvider
from app.repositories.match_repository import MatchRepository


@dataclass
class CollectRunResult:
    """
    Accounts for every row's fate - nothing is silently dropped.
    """

    code: str
    season: str
    fetched: int = 0
    saved: int = 0
    skipped_missing_field: int = 0
    skipped_unparseable: int = 0
    skipped_unmapped_home: int = 0
    skipped_unmapped_away: int = 0
    skipped_duplicate: int = 0
    unmatched_teams: set = field(default_factory=set)


class FootballDataCoUkCollector:
    def __init__(self, team_map: dict[str, dict[str, str]]):
        self.provider = FootballDataCoUkProvider()
        self.repository = MatchRepository()
        self.team_map = team_map

    def _existing_keys(self, competition: str) -> set[tuple]:
        """
        Dedupe index of football-data.org-sourced rows already on
        record for this competition, keyed by (date, home, away).
        football-data.org wins any collision - it has real ids, this
        source doesn't. Rows already collected from
        football-data.co.uk in a prior run are excluded from this
        index on purpose: they're identified again by the same
        deterministic id and simply overwritten with themselves by
        the merge-by-id save, which is what makes re-running this
        collector safe.
        """

        existing = set()

        for match in self.repository.get_all_historical_matches():
            if match.get("competition") != competition:
                continue

            if match.get("source", "football-data.org") != "football-data.org":
                continue

            date = (match.get("utc_date") or match.get("kickoff") or "")[:10]
            existing.add((date, match.get("home_team"), match.get("away_team")))

        return existing

    def collect(
        self,
        code: str,
        season: str,
        season_start_year: int,
    ) -> CollectRunResult:
        result = CollectRunResult(code=code, season=season)
        team_map = self.team_map.get(code, {})
        competition = COMPETITION_CODE_MAP[code]

        csv_text = self.provider.fetch_season_csv(code, season)
        rows = parse_csv_rows(csv_text)
        result.fetched = len(rows)

        existing_keys = self._existing_keys(competition)
        to_save = []

        for row in rows:
            record, reason = normalize_row(row, code, season_start_year, team_map)

            if record is None:
                if reason == "unmapped_home_team":
                    result.skipped_unmapped_home += 1
                    result.unmatched_teams.add(row.get("HomeTeam", ""))
                elif reason == "unmapped_away_team":
                    result.skipped_unmapped_away += 1
                    result.unmatched_teams.add(row.get("AwayTeam", ""))
                elif reason == "missing_field":
                    result.skipped_missing_field += 1
                else:
                    result.skipped_unparseable += 1
                continue

            key = (record["utc_date"][:10], record["home_team"], record["away_team"])

            if key in existing_keys:
                result.skipped_duplicate += 1
                continue

            to_save.append(record)

        if to_save:
            self.repository.save_historical_matches(to_save)

        result.saved = len(to_save)

        return result

    def close(self) -> None:
        self.provider.close()
