from app.repositories.team_repository import TeamRepository


def make_repo(tmp_path):
    repo = TeamRepository()
    repo.data_file = tmp_path / "teams.json"
    repo.data_file.write_text("[]", encoding="utf-8")

    return repo


def team(id, name, league):
    return {
        "id": id,
        "name": name,
        "country": "England",
        "league": league,
        "stadium": "Some Stadium",
        "manager": "Some Manager",
    }


def test_saving_a_second_league_does_not_erase_the_first(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_teams([team(57, "Arsenal FC", "Premier League")])
    repo.save_teams([team(81, "FC Barcelona", "Primera Division")])

    ids = {t["id"] for t in repo.get_all()}

    assert ids == {57, 81}


def test_saving_an_existing_id_updates_it_in_place(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_teams([team(57, "Arsenal FC", "Premier League")])
    repo.save_teams([team(57, "Arsenal FC", "Champions League")])

    teams = repo.get_all()

    assert len(teams) == 1
    assert teams[0]["league"] == "Champions League"


def test_get_by_name_is_case_insensitive(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_teams([team(57, "Arsenal FC", "Premier League")])

    assert repo.get_by_name("arsenal fc")["id"] == 57
