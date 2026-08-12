from app.reasoning.reasoning_models import ReasoningResult


def explain(result: ReasoningResult) -> list[str]:
    """
    Convert structured reasoning into readable, labelled explanations.
    """

    explanations = []

    explanations.extend(f"Strength: {s}" for s in result.strengths)
    explanations.extend(f"Opportunity: {o}" for o in result.opportunities)
    explanations.extend(f"Risk: {r}" for r in result.risks)
    explanations.extend(f"Weakness: {w}" for w in result.weaknesses)
    explanations.extend(f"Contradiction: {c}" for c in result.contradictions)

    return explanations


def _favour_strength(probability: float) -> str:
    if probability >= 75:
        return "strongly"
    if probability >= 60:
        return "clearly"
    return "slightly"


def _confidence_phrase(confidence: float) -> str:
    if confidence >= 70:
        return "a high-confidence prediction"
    if confidence >= 45:
        return "a moderate-confidence prediction"
    return "a low-confidence prediction"


def _lowercase_first(text: str) -> str:
    if not text:
        return text

    return (text[0].lower() + text[1:]).rstrip(".")


def _personalize(text: str, home_team: str, away_team: str) -> str:
    """
    reasoning_rules.py writes its findings generically ("Home team
    concedes more goals.") since it has no notion of club names. That's
    fine for the labelled `explanation` list, but ambiguous inside a
    narrative that already names both clubs - "Team X are favoured
    because home team concedes more goals" doesn't say whose defence
    that is. Only used for the narrative; `explain()`'s output is
    untouched.
    """

    text = text.replace("Home team", home_team)
    text = text.replace("the home team", home_team)
    text = text.replace("Away team", away_team)
    text = text.replace("the away team", away_team)

    return text


def _reason_clause(text: str, home_team: str, away_team: str) -> str:
    """
    Personalize a reasoning_rules.py string and fold it into a
    lowercase mid-sentence clause - unless personalizing put a club
    name at the start, in which case that capitalization has to stay
    (lowercasing "Arsenal FC" would be wrong, lowercasing "Historical"
    is fine).
    """

    personalized = _personalize(text, home_team, away_team)

    if personalized.startswith(home_team) or personalized.startswith(away_team):
        return personalized.rstrip(".")

    return _lowercase_first(personalized)


def summarize(
    winner: str,
    probability: float,
    confidence: float,
    reasoning: ReasoningResult,
) -> str:
    """
    Produce a short, human-readable narrative describing the
    prediction - the kind of summary a sports analyst would give,
    built entirely from the same structured reasoning behind the
    numeric result (no information is introduced here that isn't
    already in `reasoning`).
    """

    pro_home = reasoning.strengths + reasoning.opportunities
    pro_away = reasoning.weaknesses + reasoning.risks

    sentences = []

    if winner == "DRAW":
        sentences.append(
            f"{reasoning.home_team} and {reasoning.away_team} look "
            "evenly matched, with no side holding a clear edge."
        )
        counter_reasons = pro_home + pro_away
    else:
        if winner == "HOME":
            favoured, leading_reasons, counter_reasons = (
                reasoning.home_team,
                pro_home,
                pro_away,
            )
        else:
            favoured, leading_reasons, counter_reasons = (
                reasoning.away_team,
                pro_away,
                pro_home,
            )

        if leading_reasons:
            reason = _reason_clause(
                leading_reasons[0], reasoning.home_team, reasoning.away_team
            )
            sentences.append(
                f"{favoured} are {_favour_strength(probability)} "
                f"favoured because {reason}."
            )
        else:
            sentences.append(
                f"{favoured} are favoured, though the supporting "
                "evidence is thin."
            )

    if counter_reasons:
        reason = _reason_clause(
            counter_reasons[0], reasoning.home_team, reasoning.away_team
        )
        sentences.append(
            f"However, {reason}, which creates meaningful uncertainty."
        )

    if reasoning.contradictions:
        sentences.append(
            "Some evidence is directly contradictory, adding "
            "further uncertainty."
        )

    sentences.append(
        f"This is considered {_confidence_phrase(confidence)} "
        f"({confidence:.0f}% confidence)."
    )

    return " ".join(sentences)
