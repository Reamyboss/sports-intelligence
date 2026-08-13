import { Link } from 'react-router-dom'
import type { Match } from '../api/types'

interface MatchCardProps {
  match: Match
}

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase()

  const styles: Record<string, string> = {
    scheduled: 'bg-[var(--accent-soft)] text-[var(--accent)]',
    timed: 'bg-[var(--accent-soft)] text-[var(--accent)]',
    finished: 'bg-[var(--border)] text-[var(--text-muted)]',
    postponed: 'bg-[var(--warn-soft)] text-[var(--warn)]',
    live: 'bg-[var(--away-soft)] text-[var(--away)]',
  }

  const style = styles[normalized] ?? 'bg-[var(--border)] text-[var(--text-muted)]'

  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${style}`}>
      {normalized}
    </span>
  )
}

export function MatchCard({ match }: MatchCardProps) {
  const played = match.home_score !== null && match.away_score !== null

  let kickoffLabel: string

  try {
    kickoffLabel = dateFormatter.format(new Date(match.kickoff))
  } catch {
    kickoffLabel = match.kickoff
  }

  return (
    <Link
      to={`/matches/${match.id}`}
      className="block rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 transition-colors hover:border-[var(--accent)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)] sm:p-5"
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <span className="truncate text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
          {match.competition}
        </span>
        <StatusBadge status={match.status} />
      </div>

      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0 flex-1 space-y-1">
          <p className="truncate font-medium text-[var(--text)]">{match.home_team}</p>
          <p className="truncate font-medium text-[var(--text)]">{match.away_team}</p>
        </div>

        {played && (
          <div className="flex flex-col items-end gap-1 text-sm font-semibold text-[var(--text)] tabular-nums">
            <span>{match.home_score}</span>
            <span>{match.away_score}</span>
          </div>
        )}
      </div>

      <p className="mt-3 text-xs text-[var(--text-muted)]">{kickoffLabel}</p>
    </Link>
  )
}
