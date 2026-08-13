"""
Aggregate metrics computed from a list of BacktestResult.

No metric here is invented to fill a gap - where the underlying data
doesn't support a standard metric (e.g. a full 3-class Brier score,
which needs a probability for every outcome, not just the predicted
one), that limitation is reported explicitly instead.
"""

from collections import Counter
from dataclasses import dataclass

from app.backtesting.runner import BacktestResult

CLASSES = ("HOME", "DRAW", "AWAY")

CONFIDENCE_BUCKETS = [
    (0, 39, "0-39%"),
    (40, 49, "40-49%"),
    (50, 59, "50-59%"),
    (60, 69, "60-69%"),
    (70, 79, "70-79%"),
    (80, 100, "80-100%"),
]


def _accuracy(predictions: list[str], actuals: list[str]) -> float:
    if not predictions:
        return 0.0
    correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
    return round(correct / len(predictions) * 100, 2)


def _per_class_accuracy(predictions: list[str], actuals: list[str]) -> dict:
    out = {}
    for cls in CLASSES:
        cls_indices = [i for i, a in enumerate(actuals) if a == cls]
        if not cls_indices:
            out[cls] = None
            continue
        correct = sum(1 for i in cls_indices if predictions[i] == cls)
        out[cls] = round(correct / len(cls_indices) * 100, 2)
    return out


def _distribution(predictions: list[str]) -> dict:
    total = len(predictions)
    counts = Counter(predictions)
    return {
        cls: round(counts.get(cls, 0) / total * 100, 2) if total else 0.0
        for cls in CLASSES
    }


def _single_class_brier(probabilities: list[float], correct: list[bool]) -> float:
    """
    Not a full multi-class Brier score - the system only outputs a
    probability for the *predicted* class, not a distribution over
    all three outcomes, so the classic 3-way formula isn't computable
    from this data. This is the single-class variant: how well does
    "probability assigned to the predicted outcome" track whether
    that outcome actually happened. 0 is perfect, 1 is worst possible.
    """

    n = len(probabilities)
    if n == 0:
        return 0.0

    total = 0.0
    for p, was_correct in zip(probabilities, correct):
        p_fraction = p / 100.0
        outcome = 1.0 if was_correct else 0.0
        total += (p_fraction - outcome) ** 2

    return round(total / n, 4)


def _confidence_buckets(confidences: list[float], correct: list[bool]) -> list[dict]:
    rows = []
    for low, high, label in CONFIDENCE_BUCKETS:
        indices = [i for i, c in enumerate(confidences) if low <= c <= high]
        n = len(indices)
        acc = (
            round(sum(1 for i in indices if correct[i]) / n * 100, 2)
            if n > 0
            else None
        )
        rows.append({"bucket": label, "count": n, "accuracy": acc})
    return rows


@dataclass
class Metrics:
    total: int
    competitions: dict

    baseline_accuracy: float
    current_accuracy: float
    baseline_per_class: dict
    current_per_class: dict
    baseline_distribution: dict
    current_distribution: dict

    changed_count: int
    changed_became_correct: int
    changed_became_incorrect: int
    changed_net: int

    baseline_brier: float
    current_brier: float
    baseline_avg_probability: float
    current_avg_probability: float
    baseline_confidence_buckets: list
    current_confidence_buckets: list

    avg_evidence_items: float
    pct_zero_evidence: float
    pct_1plus_evidence: float
    pct_2plus_evidence: float
    pct_evidence_agreement: float
    pct_evidence_disagreement: float


def compute_metrics(results: list[BacktestResult]) -> Metrics:
    total = len(results)

    actuals = [r.actual for r in results]
    baseline_preds = [r.baseline_prediction for r in results]
    current_preds = [r.current_prediction for r in results]

    baseline_correct = [p == a for p, a in zip(baseline_preds, actuals)]
    current_correct = [p == a for p, a in zip(current_preds, actuals)]

    changed = [
        i
        for i in range(total)
        if baseline_preds[i] != current_preds[i]
    ]
    became_correct = sum(
        1 for i in changed if not baseline_correct[i] and current_correct[i]
    )
    became_incorrect = sum(
        1 for i in changed if baseline_correct[i] and not current_correct[i]
    )

    evidence_counts = [r.evidence_count for r in results]

    competitions = dict(Counter(r.competition for r in results))

    return Metrics(
        total=total,
        competitions=competitions,
        baseline_accuracy=_accuracy(baseline_preds, actuals),
        current_accuracy=_accuracy(current_preds, actuals),
        baseline_per_class=_per_class_accuracy(baseline_preds, actuals),
        current_per_class=_per_class_accuracy(current_preds, actuals),
        baseline_distribution=_distribution(baseline_preds),
        current_distribution=_distribution(current_preds),
        changed_count=len(changed),
        changed_became_correct=became_correct,
        changed_became_incorrect=became_incorrect,
        changed_net=became_correct - became_incorrect,
        baseline_brier=_single_class_brier(
            [r.baseline_probability for r in results], baseline_correct
        ),
        current_brier=_single_class_brier(
            [r.current_probability for r in results], current_correct
        ),
        baseline_avg_probability=round(
            sum(r.baseline_probability for r in results) / total, 2
        ) if total else 0.0,
        current_avg_probability=round(
            sum(r.current_probability for r in results) / total, 2
        ) if total else 0.0,
        baseline_confidence_buckets=_confidence_buckets(
            [r.baseline_confidence for r in results], baseline_correct
        ),
        current_confidence_buckets=_confidence_buckets(
            [r.current_confidence for r in results], current_correct
        ),
        avg_evidence_items=round(sum(evidence_counts) / total, 2) if total else 0.0,
        pct_zero_evidence=round(
            sum(1 for c in evidence_counts if c == 0) / total * 100, 2
        ) if total else 0.0,
        pct_1plus_evidence=round(
            sum(1 for c in evidence_counts if c >= 1) / total * 100, 2
        ) if total else 0.0,
        pct_2plus_evidence=round(
            sum(1 for c in evidence_counts if c >= 2) / total * 100, 2
        ) if total else 0.0,
        pct_evidence_agreement=round(
            sum(
                1
                for r in results
                if (r.home_support > 0) != (r.away_support > 0)
                and (r.home_support + r.away_support) > 0
            )
            / total
            * 100,
            2,
        ) if total else 0.0,
        pct_evidence_disagreement=round(
            sum(1 for r in results if r.home_support > 0 and r.away_support > 0)
            / total
            * 100,
            2,
        ) if total else 0.0,
    )


def format_report(m: Metrics) -> str:
    lines = []
    lines.append(f"Total matches: {m.total}")
    lines.append(f"Competitions: {m.competitions}")
    lines.append("")
    lines.append(f"Overall accuracy - baseline: {m.baseline_accuracy}%  current: {m.current_accuracy}%")
    lines.append(f"Per-class (baseline): {m.baseline_per_class}")
    lines.append(f"Per-class (current):  {m.current_per_class}")
    lines.append(f"Distribution (baseline): {m.baseline_distribution}")
    lines.append(f"Distribution (current):  {m.current_distribution}")
    lines.append("")
    lines.append(f"Changed predictions: {m.changed_count}")
    lines.append(f"  became correct:   {m.changed_became_correct}")
    lines.append(f"  became incorrect: {m.changed_became_incorrect}")
    lines.append(f"  net:              {m.changed_net}")
    lines.append("")
    lines.append(f"Single-class Brier - baseline: {m.baseline_brier}  current: {m.current_brier}")
    lines.append(f"Avg probability - baseline: {m.baseline_avg_probability}  current: {m.current_avg_probability}")
    lines.append(f"Confidence buckets (baseline): {m.baseline_confidence_buckets}")
    lines.append(f"Confidence buckets (current):  {m.current_confidence_buckets}")
    lines.append("")
    lines.append(f"Avg evidence items: {m.avg_evidence_items}")
    lines.append(f"% zero evidence: {m.pct_zero_evidence}")
    lines.append(f"% 1+ evidence:   {m.pct_1plus_evidence}")
    lines.append(f"% 2+ evidence:   {m.pct_2plus_evidence}")
    lines.append(f"% agreement:     {m.pct_evidence_agreement}")
    lines.append(f"% disagreement:  {m.pct_evidence_disagreement}")
    return "\n".join(lines)
