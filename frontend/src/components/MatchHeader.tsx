import type { Match } from '../api/types'

interface MatchHeaderProps {
  match: Match
}

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

export function MatchHeader({ match }: MatchHeaderProps) {
  const played = match.home_score !== null && match.away_score !== null

  let kickoffLabel: string

  try {
    kickoffLabel = dateFormatter.format(new Date(match.kickoff))
  } catch {
    kickoffLabel = match.kickoff
  }

  return (
    <header className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
        {match.competition} · {kickoffLabel}
      </p>

      <div className="mt-3 flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold text-[var(--text)] sm:text-2xl">
          {match.home_team}
          <span className="mx-2 font-normal text-[var(--text-muted)]">vs</span>
          {match.away_team}
        </h1>

        {played && (
          <p className="shrink-0 text-xl font-semibold tabular-nums text-[var(--text)] sm:text-2xl">
            {match.home_score}–{match.away_score}
          </p>
        )}
      </div>

      <p className="mt-2 text-sm capitalize text-[var(--text-muted)]">{match.status}</p>
    </header>
  )
}
