import json
from datetime import datetime
from pathlib import Path

from app.utils.helpers import parse_kickoff

# Every MatchRepository() call site (there are many - each evidence
# module owns its own instance) re-reads matches.json/
# historical_matches.json from disk. That was fine at a few thousand
# records; past ~20k it made a single prediction take several
# seconds. Cached here by resolved file path (not per-instance) so
# every repository benefits, keyed with the file's own mtime so a
# write is always picked up on the next read - never a second stale
# copy of the data.
_file_cache: dict[Path, tuple[float, list]] = {}

# Keyed by (matches_file, historical_matches_file) - get_finished_matches_by_team
# used to re-scan every match in both files on every single call, which
# is O(n) per lookup and every evidence module makes several lookups
# per team per prediction. At a few thousand matches that was
# unnoticeable; past ~20k it made backtesting effectively O(n^2). This
# index groups the same, already-deduplicated finished matches by team
# once, so a lookup becomes O(matches for that team) instead of
# O(all matches) - same output, same order, just not recomputed from
# scratch every time.
_team_index_cache: dict[tuple[Path, Path], tuple[float, float, dict[str, list]]] = {}


def _team_index(matches_file: Path, historical_matches_file: Path) -> dict[str, list[dict]]:
    matches_mtime = matches_file.stat().st_mtime if matches_file.exists() else 0.0
    historical_mtime = (
        historical_matches_file.stat().st_mtime if historical_matches_file.exists() else 0.0
    )

    key = (matches_file, historical_matches_file)
    cached = _team_index_cache.get(key)

    if cached is not None and cached[0] == matches_mtime and cached[1] == historical_mtime:
        return cached[2]

    # Deduplicate by id before anything else. The two files are not
    # disjoint: every completed Champions League fixture is written to
    # both matches.json (as a current-season fixture) and
    # historical_matches.json (as a completed match), so a plain
    # concatenation counted all 189 of them twice. That inflated form,
    # goals, streak and head-to-head evidence for 36 clubs - up to a
    # quarter of a top side's entire history - and, because those are
    # exactly Europe's strongest teams, it skewed the evidence for the
    # matches that matter most. The duplicate rows are byte-identical
    # in teams, scores and dates, so keeping the first occurrence
    # loses nothing.
    combined = list(
        {
            match["id"]: match
            for match in (
                _read_json_cached(matches_file)
                + _read_json_cached(historical_matches_file)
            )
        }.values()
    )

    finished = [match for match in combined if match["status"].lower() == "finished"]

    for match in finished:
        match.setdefault("kickoff", match.get("utc_date"))

    index: dict[str, list[dict]] = {}

    for match in finished:
        index.setdefault(match["home_team"], []).append(match)
        index.setdefault(match["away_team"], []).append(match)

    _team_index_cache[key] = (matches_mtime, historical_mtime, index)

    return index


def _read_json_cached(path: Path) -> list:
    if not path.exists():
        return []

    mtime = path.stat().st_mtime
    cached = _file_cache.get(path)

    if cached is not None and cached[0] == mtime:
        return cached[1]

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    _file_cache[path] = (mtime, data)

    return data


def _write_json_cached(path: Path, data: list) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    # Set the cache from the data just written rather than relying on
    # the new mtime alone - two writes in quick succession can land
    # within the same filesystem mtime tick, which would otherwise
    # let a stale read slip through.
    _file_cache[path] = (path.stat().st_mtime, data)


class MatchRepository:
    def __init__(self):
        data_dir = Path(__file__).parent.parent / "data"

        self.matches_file = data_dir / "matches.json"

        self.historical_matches_file = (
            data_dir / "historical_matches.json"
        )

    # -----------------------------
    # Current Season Matches
    # -----------------------------

    def get_all_matches(self) -> list[dict]:
        # A shallow copy: callers must never be able to corrupt the
        # shared cache by mutating the list itself (append/remove).
        # Individual dicts are still shared for performance - the one
        # in-place mutation elsewhere in this codebase
        # (get_finished_matches_by_team's kickoff setdefault) is
        # idempotent, so a cached copy of that mutation is harmless.
        return list(_read_json_cached(self.matches_file))

    def get_match(
        self,
        match_id: int,
    ) -> dict | None:
        for match in self.get_all_matches():
            if match["id"] == match_id:
                return match

        return None

    def get_matches_by_competition(
        self,
        competition: str,
    ) -> list[dict]:
        return [
            match
            for match in self.get_all_matches()
            if match["competition"] == competition
        ]

    def get_matches_by_team(
        self,
        team: str,
    ) -> list[dict]:
        return [
            match
            for match in self.get_all_matches()
            if match["home_team"] == team
            or match["away_team"] == team
        ]

    def get_finished_matches_by_team(
        self,
        team: str,
        before: datetime | None = None,
        exclude_match_id: int | None = None,
    ) -> list[dict]:
        """
        Finished matches involving `team`.

        `before`, when given, excludes any match whose kickoff is not
        strictly earlier than it - and excludes matches with a
        missing/unparseable kickoff entirely, rather than guessing.
        `exclude_match_id` always excludes that match by id, regardless
        of its date, so a match can never contribute evidence to its
        own prediction.
        """

        finished = list(
            _team_index(self.matches_file, self.historical_matches_file).get(team, [])
        )

        if exclude_match_id is not None:
            finished = [
                match
                for match in finished
                if match.get("id") != exclude_match_id
            ]

        if before is not None:
            bounded = []

            for match in finished:
                kickoff = parse_kickoff(match)

                if kickoff is not None and kickoff < before:
                    bounded.append(match)

            finished = bounded

        return finished

    def save_matches(
        self,
        matches: list[dict],
    ) -> None:
        merged = {
            match["id"]: match
            for match in self.get_all_matches()
        }

        for match in matches:
            merged[match["id"]] = match

        _write_json_cached(self.matches_file, list(merged.values()))

    # -----------------------------
    # Historical Matches
    # -----------------------------

    def get_all_historical_matches(self) -> list[dict]:
        return list(_read_json_cached(self.historical_matches_file))

    def save_historical_matches(
        self,
        matches: list[dict],
    ) -> None:
        merged = {
            match["id"]: match
            for match in self.get_all_historical_matches()
        }

        for match in matches:
            merged[match["id"]] = match

        _write_json_cached(self.historical_matches_file, list(merged.values()))