from datetime import datetime

from app.evidence.evidence_models import Evidence
from app.evidence.form_evidence import get_recent_form
from app.evidence.goal_evidence import get_goal_statistics
from app.evidence.h2h_evidence import get_head_to_head
from app.evidence.home_away_evidence import get_home_away_statistics
from app.evidence.streak_evidence import get_current_streak
from app.knowledge.match_profile import MatchProfile


def build_evidence(
    profile: MatchProfile,
    match_id: int,
    kickoff: datetime,
) -> dict:
    """
    `match_id` and `kickoff` scope every evidence query to matches
    strictly before this match, excluding this match itself - so a
    prediction can never use its own result (or a later result) as
    evidence.
    """

    return {
        "home_team": {
            "name": profile.home_team,
            "form": get_recent_form(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "goals": get_goal_statistics(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "home_away": get_home_away_statistics(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "streak": get_current_streak(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "rest_days": profile.rest_days_home,
        },
        "away_team": {
            "name": profile.away_team,
            "form": get_recent_form(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "goals": get_goal_statistics(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "home_away": get_home_away_statistics(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "streak": get_current_streak(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "rest_days": profile.rest_days_away,
        },
        "head_to_head": get_head_to_head(
            profile.home_team,
            profile.away_team,
            before=kickoff,
            exclude_match_id=match_id,
        ),
    }


def build_supporting_evidence(evidence: dict) -> list[Evidence]:
    """
    Convert the evidence dict `build_evidence()` already produced into
    structured Evidence objects. Introduces no new data source and no
    new temporal risk - every value here traces directly to fields
    already computed under the same before/exclude_match_id boundary.

    A signal is only reported when there is a real difference to
    report; ties and empty samples are omitted rather than reported
    as a fabricated zero. `rest_days` is real (app/knowledge/rest_days.py,
    computed under the same before/exclude_match_id boundary as
    everything else) but only becomes a signal when both teams have a
    computable value - a missing prior match (None) is never treated
    as zero rest.
    """

    items: list[Evidence] = []

    home = evidence["home_team"]
    away = evidence["away_team"]
    home_name = home["name"]
    away_name = away["name"]

    # --- Recent form ---
    home_wins = home["form"].count("W")
    away_wins = away["form"].count("W")

    if (home["form"] or away["form"]) and home_wins != away_wins:
        home_favoured = home_wins > away_wins
        leader = home_name if home_favoured else away_name

        items.append(
            Evidence(
                title="Recent Form",
                supports="HOME" if home_favoured else "AWAY",
                strength=float(abs(home_wins - away_wins)),
                reason=(
                    f"{leader} has more wins in recent matches "
                    f"({home_wins} of {len(home['form'])} for {home_name} "
                    f"vs {away_wins} of {len(away['form'])} for {away_name})."
                ),
            )
        )

    # --- Goals scored ---
    home_avg = home["goals"]["avg_goals_scored"]
    away_avg = away["goals"]["avg_goals_scored"]

    if (
        home["goals"]["matches"] > 0 or away["goals"]["matches"] > 0
    ) and home_avg != away_avg:
        home_favoured = home_avg > away_avg
        leader = home_name if home_favoured else away_name

        items.append(
            Evidence(
                title="Goals Scored",
                supports="HOME" if home_favoured else "AWAY",
                strength=round(abs(home_avg - away_avg), 2),
                reason=(
                    f"{leader} averages more goals scored "
                    f"({home_avg:.2f} vs {away_avg:.2f})."
                ),
            )
        )

    # --- Head-to-head ---
    h2h = evidence["head_to_head"]

    if h2h["matches"] > 0 and h2h["home_wins"] != h2h["away_wins"]:
        home_favoured = h2h["home_wins"] > h2h["away_wins"]
        leader = home_name if home_favoured else away_name

        items.append(
            Evidence(
                title="Head-to-Head",
                supports="HOME" if home_favoured else "AWAY",
                strength=float(abs(h2h["home_wins"] - h2h["away_wins"])),
                reason=(
                    f"{leader} leads the head-to-head record "
                    f"({h2h['home_wins']}-{h2h['draws']}-{h2h['away_wins']} "
                    f"in {h2h['matches']} meetings)."
                ),
            )
        )

    # --- Current streak ---
    home_streak = home["streak"]
    away_streak = away["streak"]

    home_net = home_streak["winning_streak"] - home_streak["losing_streak"]
    away_net = away_streak["winning_streak"] - away_streak["losing_streak"]

    if (
        home_streak["last_10_results"] or away_streak["last_10_results"]
    ) and home_net != away_net:
        home_favoured = home_net > away_net
        leader = home_name if home_favoured else away_name

        items.append(
            Evidence(
                title="Current Streak",
                supports="HOME" if home_favoured else "AWAY",
                strength=float(abs(home_net - away_net)),
                reason=(
                    f"{leader} is on a stronger current run (winning streak "
                    f"{home_streak['winning_streak']} vs "
                    f"{away_streak['winning_streak']}, losing streak "
                    f"{home_streak['losing_streak']} vs "
                    f"{away_streak['losing_streak']})."
                ),
            )
        )

    # --- Home/away context ---
    home_at_home = home["home_away"]["home"]
    away_at_away = away["home_away"]["away"]

    home_at_home_played = sum(home_at_home.values())
    away_at_away_played = sum(away_at_away.values())

    if home_at_home_played > 0 and away_at_away_played > 0:
        home_rate = home_at_home["wins"] / home_at_home_played
        away_rate = away_at_away["wins"] / away_at_away_played

        if home_rate != away_rate:
            home_favoured = home_rate > away_rate
            leader = home_name if home_favoured else away_name

            items.append(
                Evidence(
                    title="Home/Away Record",
                    supports="HOME" if home_favoured else "AWAY",
                    strength=round(abs(home_rate - away_rate), 2),
                    reason=(
                        f"{home_name} win {home_rate:.0%} of home matches; "
                        f"{away_name} win {away_rate:.0%} of away matches."
                    ),
                )
            )

    # --- Rest days ---
    home_rest = home["rest_days"]
    away_rest = away["rest_days"]

    if (
        home_rest is not None
        and away_rest is not None
        and home_rest != away_rest
    ):
        home_favoured = home_rest > away_rest
        leader = home_name if home_favoured else away_name

        items.append(
            Evidence(
                title="Rest Days",
                supports="HOME" if home_favoured else "AWAY",
                strength=float(abs(home_rest - away_rest)),
                reason=(
                    f"{leader} had more rest before this match "
                    f"({home_rest} days for {home_name} vs "
                    f"{away_rest} days for {away_name})."
                ),
            )
        )

    return items
