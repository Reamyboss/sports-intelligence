from app.collectors.normalizer import normalize_team


def make_raw_team(**overrides):
    raw = {
        "id": 57,
        "name": "Arsenal FC",
        "area": {"name": "England"},
        "venue": "Emirates Stadium",
        "coach": {"name": "Mikel Arteta"},
        "runningCompetitions": [
            {"code": "COM", "name": "FA Community Shield"},
            {"code": "PL", "name": "Premier League"},
        ],
    }
    raw.update(overrides)
    return raw


def test_normalize_team_maps_expected_fields():
    team = normalize_team(make_raw_team(), competition_code="PL")

    assert team == {
        "id": 57,
        "name": "Arsenal FC",
        "country": "England",
        "league": "Premier League",
        "stadium": "Emirates Stadium",
        "manager": "Mikel Arteta",
    }


def test_normalize_team_uses_the_synced_competition_not_the_first_one():
    """
    A team can be listed under several runningCompetitions (e.g. a
    domestic league plus a cup). The league field should reflect
    whichever competition this sync call was actually for.
    """

    team = normalize_team(make_raw_team(), competition_code="COM")

    assert team["league"] == "FA Community Shield"


def test_normalize_team_falls_back_to_code_if_competition_not_listed():
    team = normalize_team(make_raw_team(), competition_code="CL")

    assert team["league"] == "CL"


def test_normalize_team_handles_missing_coach():
    team = normalize_team(make_raw_team(coach={"name": None}), competition_code="PL")

    assert team["manager"] == "Unknown"


def test_normalize_team_handles_null_coach_object():
    team = normalize_team(make_raw_team(coach=None), competition_code="PL")

    assert team["manager"] == "Unknown"


def test_normalize_team_handles_missing_venue():
    team = normalize_team(make_raw_team(venue=None), competition_code="PL")

    assert team["stadium"] == "Unknown"
