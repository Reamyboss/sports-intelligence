"""
Generate ready-to-post X content from real predictions.

    python scripts/generate_x_posts.py                       # Premier League
    python scripts/generate_x_posts.py --competition "La Liga" --picks 5

Writes nothing to X. Prints Markdown (also saved to --out) for a human
to review before anything is posted:

- PICKS: the next N scheduled fixtures, posted before kickoff.
- RECEIPTS: the last N finished fixtures, graded against what the model
  would have said before kickoff (evidence is built under the same
  temporal boundary, so no result leaks into its own prediction).
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.predictions import get_prediction  # noqa: E402
from app.services.match_service import MatchService  # noqa: E402
from app.social.x_posts import (  # noqa: E402
    pick_post,
    receipt_post,
    scoreboard_post,
    x_length,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--competition", default="Premier League")
    parser.add_argument("--picks", type=int, default=5)
    parser.add_argument("--receipts", type=int, default=10)
    parser.add_argument("--out", default="x_posts_preview.md")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    matches = [
        m
        for m in MatchService().list_matches()
        if m.competition == args.competition
    ]
    upcoming = sorted(
        (m for m in matches if m.status in ("scheduled", "timed") and m.kickoff > now),
        key=lambda m: m.kickoff,
    )[: args.picks]
    finished = sorted(
        (m for m in matches if m.status == "finished" and m.home_score is not None),
        key=lambda m: m.kickoff,
        reverse=True,
    )[: args.receipts]

    out = [f"# X posts: {args.competition}", ""]

    out += ["## Picks (post before kickoff)", ""]
    for m in upcoming:
        prediction = get_prediction(m.id)
        label = m.kickoff.strftime("%a %d %b, %H:%M UTC")
        post = pick_post(prediction, m.home_team, m.away_team, args.competition, label)
        out += [f"### {m.home_team} vs {m.away_team} ({x_length(post)}/280)", "", "```", post, "```", ""]

    out += ["## Receipts (quote-tweet the pick after FT)", ""]
    hits = 0
    for m in finished:
        prediction = get_prediction(m.id)
        post = receipt_post(prediction, m.home_team, m.away_team, m.home_score, m.away_score)
        hits += post.startswith("✅")
        out += [f"### {m.home_team} vs {m.away_team} ({x_length(post)}/280)", "", "```", post, "```", ""]

    if finished:
        out += ["## Scoreboard", "", "```", scoreboard_post(hits, len(finished)), "```", ""]

    text = "\n".join(out)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
