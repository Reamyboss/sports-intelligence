"""
Guards against a malformed upstream `status`.

football-data.org intermittently returns the fixture's kick-off
timestamp where a match state belongs - observed live on 54 Primeira
Liga and 1 Brasileirao fixtures. Because `status` is what decides
whether a played match becomes historical evidence, storing the raw
value means the result never feeds back into the engine.
"""

import pytest

from app.collectors.normalizer import normalize_status

VALID_STATUSES = {
    "scheduled",
    "timed",
    "in_play",
    "paused",
    "finished",
    "postponed",
    "suspended",
    "cancelled",
    "awarded",
}


# -----------------------------
# Legitimate statuses pass through
# -----------------------------


@pytest.mark.parametrize("status", sorted(VALID_STATUSES))
def test_known_statuses_are_preserved(status):
    assert normalize_status(status) == status


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("FINISHED", "finished"),
        ("Scheduled", "scheduled"),
        ("  TIMED  ", "timed"),
    ],
)
def test_known_statuses_are_normalised_to_lowercase(raw, expected):
    assert normalize_status(raw) == expected


# -----------------------------
# The exact upstream corruption
# -----------------------------


@pytest.mark.parametrize(
    "corrupt",
    [
        "2026-08-22 14:30:00Z",
        "2026-09-06 15:00:00z",
        "2026-08-15 19:30:00Z",
    ],
)
def test_timestamp_in_the_status_field_never_survives(corrupt):
    """The precise shape of the live defect."""

    assert normalize_status(corrupt) in VALID_STATUSES


def test_corrupt_status_without_a_score_becomes_scheduled():
    """
    The safe direction. A fixture wrongly marked scheduled is merely
    invisible; one wrongly marked finished would inject a fabricated
    result into the evidence base.
    """

    assert normalize_status("2026-08-22 14:30:00Z", None, None) == "scheduled"


def test_corrupt_status_with_a_full_time_score_becomes_finished():
    """
    A full-time score line is the only reliable evidence that a match
    was actually played - so it, and nothing else, promotes an
    unrecognised status to finished.
    """

    assert normalize_status("2026-08-22 14:30:00Z", 2, 1) == "finished"


def test_a_goalless_full_time_score_still_counts_as_played():
    """0-0 is a real result, not a missing one."""

    assert normalize_status("garbage", 0, 0) == "finished"


def test_a_partial_score_does_not_imply_the_match_finished():
    assert normalize_status("garbage", 2, None) == "scheduled"
    assert normalize_status("garbage", None, 1) == "scheduled"


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_missing_status_is_handled_without_raising(empty):
    assert normalize_status(empty) == "scheduled"


# -----------------------------
# Repository-level consequence
# -----------------------------


def test_normalised_status_makes_played_matches_eligible_as_evidence():
    """
    The repository selects historical evidence with
    `status.lower() == "finished"`. A corrupted status silently fails
    that check forever, which is the real damage the guard prevents.
    """

    corrupt_but_played = normalize_status("2026-08-22 14:30:00Z", 3, 1)

    assert corrupt_but_played.lower() == "finished"
