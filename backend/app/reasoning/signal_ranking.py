"""
Ranking of already-computed evidence by magnitude.

The evidence builder assigns every signal a `strength`, but nothing
downstream used to read it - reasoning and explanation both consumed
evidence in the order the rules happened to be written in, so a
head-to-head edge worth 2.0 and a goal differential worth 0.1 carried
identical weight in the narrative.

This module introduces no new evidence and no new scoring formula. It
sorts, splits and compares the strengths that `build_supporting_evidence()`
already produced.
"""

from app.evidence.evidence_models import Evidence

# Two opposing signals are in "high" conflict when the weaker one is at
# least this fraction of the stronger - i.e. the evidence genuinely
# points both ways rather than one side merely having a token counter.
HIGH_CONFLICT_RATIO = 0.75
MODERATE_CONFLICT_RATIO = 0.40


def rank_signals(supporting_evidence: list[Evidence]) -> list[Evidence]:
    """
    Strongest signal first.

    Python's sort is stable, so signals of equal strength keep the
    order the evidence builder emitted them in - ranking never
    reshuffles genuine ties.
    """

    return sorted(
        supporting_evidence,
        key=lambda item: item.strength,
        reverse=True,
    )


def split_by_side(
    signals: list[Evidence],
    side: str,
) -> tuple[list[Evidence], list[Evidence]]:
    """
    Partition ranked signals into (supporting, opposing) relative to
    `side`, each still strongest-first.

    A DRAW has no side of its own for evidence to support, so every
    signal counts as opposing it - which is the honest reading: a draw
    is what's left when neither side's evidence wins.
    """

    if side not in ("HOME", "AWAY"):
        return [], list(signals)

    supporting = [item for item in signals if item.supports == side]
    opposing = [item for item in signals if item.supports != side]

    return supporting, opposing


def strongest(signals: list[Evidence]) -> Evidence | None:
    """First item of an already-ranked list, or None when empty."""

    return signals[0] if signals else None


def side_strength(signals: list[Evidence], side: str) -> float:
    """Strength of the single strongest signal supporting `side`."""

    strengths = [item.strength for item in signals if item.supports == side]

    return max(strengths) if strengths else 0.0


def conflict_level(signals: list[Evidence]) -> str:
    """
    How genuinely the evidence disagrees with itself: NONE, LOW,
    MODERATE or HIGH.

    Raw strengths are on different scales per signal type (a goals
    differential and a head-to-head win differential are not the same
    unit), so the two sides are compared after the same saturating
    transform the prediction engine applies - strength / (strength + 1).
    Ranking uses raw strength; only this ratio needs a common scale.
    """

    home = side_strength(signals, "HOME")
    away = side_strength(signals, "AWAY")

    if home <= 0.0 or away <= 0.0:
        return "NONE"

    home_scaled = home / (home + 1.0)
    away_scaled = away / (away + 1.0)

    ratio = min(home_scaled, away_scaled) / max(home_scaled, away_scaled)

    if ratio >= HIGH_CONFLICT_RATIO:
        return "HIGH"

    if ratio >= MODERATE_CONFLICT_RATIO:
        return "MODERATE"

    return "LOW"
