import { useEffect, useMemo, useState } from 'react'
import { getMatches } from '../api/matches'
import { getCompetitions } from '../api/competitions'
import { ApiError } from '../api/client'
import type { Competition, Match } from '../api/types'
import { MatchCard } from '../components/MatchCard'
import { CompetitionFilter } from '../components/CompetitionFilter'
import { competitionLabel } from '../lib/competitions'
import { LoadingState } from '../components/LoadingState'
import { ErrorState } from '../components/ErrorState'
import { EmptyState } from '../components/EmptyState'

type LoadState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; matches: Match[]; competitions: Competition[] }

// Rendering thousands of cards at once is unusable and there is no
// pagination, so the list is capped. Filtering by competition is the
// intended way to narrow it.
const MAX_VISIBLE = 60

export function MatchListPage() {
  const [state, setState] = useState<LoadState>({ status: 'loading' })
  const [competition, setCompetition] = useState('Premier League')

  useEffect(() => {
    load()
  }, [])

  function load() {
    setState({ status: 'loading' })

    Promise.all([getMatches(), getCompetitions()])
      .then(([matches, competitions]) => setState({ status: 'ready', matches, competitions }))
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
    () => (state.status === 'ready' ? state.competitions : []),
    [state],
  )

  const selected = useMemo(
    () => competitions.find((item) => item.name === competition) ?? null,
    [competitions, competition],
  )

  const upcoming = useMemo(() => {
    const now = Date.now()

    const scoped =
      competition === 'all'
        ? matches
        : matches.filter((match) => match.competition === competition)

    return [...scoped]
      .filter((match) => new Date(match.kickoff).getTime() > now)
      .sort((a, b) => new Date(a.kickoff).getTime() - new Date(b.kickoff).getTime())
  }, [matches, competition])

  const visible = upcoming.slice(0, MAX_VISIBLE)

  const totalUpcoming = useMemo(
    () => competitions.reduce((sum, item) => sum + item.upcoming_matches, 0),
    [competitions],
  )

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold text-[var(--text)] sm:text-3xl">
          Sports Intelligence
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--text-muted)] sm:text-base">
          Every prediction here is built from real, finished matches - form, goals, head-to-head,
          streaks and home/away records - and shows you the evidence it used. Pick a match to see
          what we think, and why.
        </p>

        {state.status === 'ready' && (
          <p className="mt-3 text-sm text-[var(--text-muted)] tabular-nums">
            {totalUpcoming.toLocaleString()} upcoming fixtures across {competitions.length}{' '}
            competitions
          </p>
        )}
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
            <p className="text-sm text-[var(--text-muted)] tabular-nums">
              {upcoming.length > MAX_VISIBLE
                ? `Showing ${MAX_VISIBLE} of ${upcoming.length}`
                : `${upcoming.length} match${upcoming.length === 1 ? '' : 'es'}`}
            </p>
          </div>

          {visible.length === 0 ? (
            selected && selected.availability !== 'ACTIVE' && selected.played_matches > 0 ? (
              // The Champions League case: a complete past season on
              // record and no new fixtures published yet. Saying "no
              // matches" here would be false.
              <EmptyState
                title={`No ${competitionLabel(selected.name)} fixtures scheduled yet`}
                message={`We hold ${selected.played_matches} completed ${competitionLabel(
                  selected.name,
                )} matches${
                  selected.season ? ` from ${selected.season}/${(selected.season + 1) % 100}` : ''
                }, and they already inform predictions for these teams elsewhere. New fixtures will appear here once the schedule is published.`}
              />
            ) : (
              <EmptyState
                title="No upcoming fixtures"
                message="Try a different competition."
              />
            )
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {visible.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
