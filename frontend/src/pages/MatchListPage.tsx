import { useEffect, useMemo, useState } from 'react'
import { getMatches } from '../api/matches'
import { ApiError } from '../api/client'
import type { Match } from '../api/types'
import { MatchCard } from '../components/MatchCard'
import { CompetitionFilter } from '../components/CompetitionFilter'
import { LoadingState } from '../components/LoadingState'
import { ErrorState } from '../components/ErrorState'
import { EmptyState } from '../components/EmptyState'

type LoadState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; matches: Match[] }

export function MatchListPage() {
  const [state, setState] = useState<LoadState>({ status: 'loading' })
  // Defaults to Premier League rather than "all" - the backend has
  // 3,640 matches across 12 competitions with no pagination, and
  // rendering all of them at once as cards is unusable. "All
  // competitions" is one click away, not hidden.
  const [competition, setCompetition] = useState('Premier League')

  useEffect(() => {
    load()
  }, [])

  function load() {
    setState({ status: 'loading' })

    getMatches()
      .then((matches) => setState({ status: 'ready', matches }))
      .catch((error: unknown) => {
        const message =
          error instanceof ApiError
            ? error.message
            : 'Something went wrong loading matches.'
        setState({ status: 'error', message })
      })
  }

  const matches = useMemo(() => (state.status === 'ready' ? state.matches : []), [state])

  const competitions = useMemo(
    () => Array.from(new Set(matches.map((match) => match.competition))).sort(),
    [matches],
  )

  const filtered = useMemo(() => {
    const scoped =
      competition === 'all' ? matches : matches.filter((match) => match.competition === competition)

    return [...scoped].sort(
      (a, b) => new Date(a.kickoff).getTime() - new Date(b.kickoff).getTime(),
    )
  }, [matches, competition])

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold text-[var(--text)] sm:text-3xl">Matches</h1>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          Select a match to see the evidence and reasoning behind its prediction.
        </p>
      </header>

      {state.status === 'loading' && <LoadingState label="Loading matches…" />}

      {state.status === 'error' && (
        <ErrorState title="Couldn't load matches" message={state.message} onRetry={load} />
      )}

      {state.status === 'ready' && (
        <>
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <CompetitionFilter
              competitions={competitions}
              value={competition}
              onChange={setCompetition}
            />
            <p className="text-sm text-[var(--text-muted)]">
              {filtered.length} match{filtered.length === 1 ? '' : 'es'}
            </p>
          </div>

          {filtered.length === 0 ? (
            <EmptyState
              title="No matches for this competition"
              message="Try a different competition."
            />
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
