"""
Turns a PredictionResult into posts for X (Twitter).

Two post types, which together make the account's whole pitch:

- PICK: posted before kickoff. The call, the probability, the top
  evidence, and - the part nobody else posts - what would make it wrong.
- RECEIPT: posted after full time, quote-tweeting the pick. Graded
  publicly, misses included. Never deleted.

Pure formatting: nothing here talks to the X API or changes a
prediction. Every post is kept within X's 280-character limit.
"""

import re

from app.prediction.prediction_models import PredictionResult

X_LIMIT = 280

# Opposition weaker than this is noise (e.g. a one-day rest difference)
# and reads badly as "what would make me wrong".
MIN_OPPOSITION_STRENGTH = 1.5

_SUFFIXES = re.compile(r"\s+(FC|AFC|CF|SC)$|^(AFC|FC)\s+")


def short_name(team: str) -> str:
    """'Arsenal FC' -> 'Arsenal', 'AFC Bournemouth' -> 'Bournemouth'."""
    return _SUFFIXES.sub("", team).strip()


def x_length(text: str) -> int:
    """
    Approximate X's weighted length: most emoji and CJK characters
    count as two.
    """
    return sum(2 if ord(ch) >= 0x1100 else 1 for ch in text)


def _shorten(text: str, home: str, away: str) -> str:
    return text.replace(home, short_name(home)).replace(away, short_name(away))


def _call(prediction: PredictionResult, home: str, away: str) -> str:
    if prediction.winner == "HOME":
        return f"{short_name(home)} win"
    if prediction.winner == "AWAY":
        return f"{short_name(away)} win"
    return "Draw"


def _fit(
    head: list[str], bullets: list[str], tail: list[str], keep: int = 0
) -> str:
    """Drop bullets from the end, down to `keep`, until the post fits."""
    bullets = list(bullets)
    while True:
        text = "\n".join(head + bullets + tail)
        if x_length(text) <= X_LIMIT or len(bullets) <= keep:
            return text
        bullets.pop()


def pick_post(
    prediction: PredictionResult,
    home: str,
    away: str,
    competition: str,
    kickoff_label: str,
) -> str:
    """The pre-kickoff post."""
    evidence = sorted(
        (
            e
            for e in prediction.reasoning.supporting_evidence
            if e.supports == prediction.winner
        ),
        key=lambda e: e.strength,
        reverse=True,
    )
    bullets = [
        f"• {_shorten(e.reason, home, away).rstrip('.')}" for e in evidence[:3]
    ]
    if not bullets:
        bullets = ["• No strong signal either way. This is a lean, not a lock"]

    opposition = prediction.strongest_opposition
    if opposition and opposition.strength >= MIN_OPPOSITION_STRENGTH:
        wrong = f"⚠️ What makes me wrong: {_shorten(opposition.reason, home, away)}"
    else:
        wrong = "⚠️ What makes me wrong: nothing in my data. That's when upsets happen"

    head = [
        f"🔮 {competition}: {short_name(home)} vs {short_name(away)}",
        kickoff_label,
        "",
        f"Call: {_call(prediction, home, away)} ({prediction.probability:.0f}%)",
        f"Confidence: {prediction.confidence:.0f}/100",
        "",
    ]
    footer = "Graded after FT. No deletes."
    text = _fit(head, bullets, ["", wrong, "", footer], keep=1)
    if x_length(text) > X_LIMIT:
        # Evidence and warning can't share the post: keep the evidence
        # and leave the warning for a reply.
        text = _fit(head, bullets, ["", footer])
    return text


def receipt_post(
    prediction: PredictionResult,
    home: str,
    away: str,
    home_score: int,
    away_score: int,
) -> str:
    """The post-full-time grade, written to quote-tweet the pick."""
    if home_score > away_score:
        actual = "HOME"
    elif away_score > home_score:
        actual = "AWAY"
    else:
        actual = "DRAW"

    hit = actual == prediction.winner
    score = f"{short_name(home)} {home_score}-{away_score} {short_name(away)}"
    called = f"{_call(prediction, home, away)} ({prediction.probability:.0f}%)"

    if hit:
        lines = [f"✅ RECEIPT: {score}", "", f"Called: {called}. Landed."]
    else:
        lines = [
            f"❌ RECEIPT: {score}",
            "",
            f"Called: {called}. Wrong.",
        ]
        opposition = prediction.strongest_opposition
        if opposition and opposition.strength >= MIN_OPPOSITION_STRENGTH:
            lines += [
                "",
                f"The warning I under-weighted: {_shorten(opposition.reason, home, away)}",
            ]
    lines += ["", "Every call stays up. That's the point."]

    text = "\n".join(lines)
    if x_length(text) > X_LIMIT:
        text = "\n".join(lines[:3] + lines[-2:])
    return text


def scoreboard_post(hits: int, total: int) -> str:
    """A running public record, e.g. for a weekly post."""
    rate = 100 * hits / total if total else 0.0
    return (
        f"📊 Public record: {hits}/{total} correct ({rate:.0f}%).\n\n"
        "Every pick posted before kickoff, graded after FT, none deleted.\n\n"
        "Most tipsters hide their misses. I pin mine."
    )
