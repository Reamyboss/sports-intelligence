def get_team_form(team_name: str) -> list[str]:
    """
    Temporary mocked form.

    Later this will query our database.
    """

    forms = {
        "Arsenal": ["W", "W", "D", "L", "W"],
        "Chelsea": ["L", "D", "W", "L", "W"],
    }

    return forms.get(team_name, [])
