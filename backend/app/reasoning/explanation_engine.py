from app.evidence.evidence_models import Evidence
from app.reasoning.reasoning_models import ReasoningResult
from app.reasoning.signal_ranking import (
    conflict_level,
    rank_signals,
    split_by_side,
    strongest,
)


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


def _lead_clause(
    signal: Evidence | None,
    fallback_rules: list[str],
    reasoning: ReasoningResult,
) -> str:
    """
    The clause the narrative should lead with.

    Prefers the strongest ranked evidence, whose `reason` already
    names the clubs and quotes the actual figures. Falls back to
    reasoning_rules.py's generic strings only when there is no ranked
    evidence at all - which keeps matches with no real evidence (and
    every test built on them) behaving exactly as before.
    """

    if signal is not None:
        return _reason_clause(
            signal.reason, reasoning.home_team, reasoning.away_team
        )

    if fallback_rules:
        return _reason_clause(
            fallback_rules[0], reasoning.home_team, reasoning.away_team
        )

    return ""


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

    The lead reason is the *strongest* evidence for the call, ranked
    by the magnitude the evidence engine computed. It used to be
    whichever rule happened to be written first in reasoning_rules.py,
    so a 0.1 goal differential could be quoted as the headline reason
    while a 5.0 streak differential went unmentioned.
    """

    ranked = rank_signals(reasoning.supporting_evidence)
    supporting, opposing = split_by_side(ranked, winner)

    pro_home = reasoning.strengths + reasoning.opportunities
    pro_away = reasoning.weaknesses + reasoning.risks

    sentences = []

    if winner == "DRAW":
        sentences.append(
            f"{reasoning.home_team} and {reasoning.away_team} look "
            "evenly matched, with no side holding a clear edge."
        )
        counter_rules = pro_home + pro_away
    else:
        if winner == "HOME":
            favoured, leading_rules, counter_rules = (
                reasoning.home_team,
                pro_home,
                pro_away,
            )
        else:
            favoured, leading_rules, counter_rules = (
                reasoning.away_team,
                pro_away,
                pro_home,
            )

        lead = _lead_clause(strongest(supporting), leading_rules, reasoning)

        if lead:
            sentences.append(
                f"{favoured} are {_favour_strength(probability)} "
                f"favoured because {lead}."
            )
        else:
            sentences.append(
                f"{favoured} are favoured, though the supporting "
                "evidence is thin."
            )

    counter = _lead_clause(strongest(opposing), counter_rules, reasoning)

    if counter:
        sentences.append(
            f"However, {counter}, which creates meaningful uncertainty."
        )

    if conflict_level(ranked) == "HIGH":
        sentences.append(
            "The evidence on both sides is close to equally strong, so "
            "this call could reasonably go the other way."
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
