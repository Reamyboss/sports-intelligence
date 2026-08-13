import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getMatch } from '../api/matches'
import { getMatchKnowledge } from '../api/knowledge'
import { getPrediction } from '../api/predictions'
import { ApiError } from '../api/client'
import type { Match, MatchProfile, PredictionResult } from '../api/types'
import { MatchHeader } from '../components/MatchHeader'
import { MatchIntelligence } from '../components/MatchIntelligence'
import { EvidenceBreakdown } from '../components/EvidenceBreakdown'
import { PredictionSummary } from '../components/PredictionSummary'
import { KeyFactors } from '../components/KeyFactors'
import { DataStatus } from '../components/DataStatus'
import { LoadingState } from '../components/LoadingState'
import { ErrorState } from '../components/ErrorState'

interface DetailData {
  match: Match
  profile: MatchProfile
  prediction: PredictionResult
}

type LoadState =
  | { status: 'loading' }
  | { status: 'not-found' }
  | { status: 'error'; message: string }
  | { status: 'ready'; data: DetailData }

export function MatchDetailPage() {
  const { id } = useParams<{ id: string }>()
  const matchId = Number(id)
  const [state, setState] = useState<LoadState>({ status: 'loading' })

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchId])

  function load() {
    if (!Number.isFinite(matchId)) {
      setState({ status: 'not-found' })
      return
    }

    setState({ status: 'loading' })

    Promise.all([getMatch(matchId), getMatchKnowledge(matchId), getPrediction(matchId)])
      .then(([match, profile, prediction]) =>
        setState({ status: 'ready', data: { match, profile, prediction } }),
      )
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 404) {
          setState({ status: 'not-found' })
          return
        }

        const message =
          error instanceof ApiError
            ? error.message
            : "Something went wrong loading this match's intelligence."
        setState({ status: 'error', message })
      })
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10">
      <Link
        to="/"
        className="mb-6 inline-block text-sm text-[var(--text-muted)] hover:text-[var(--accent)]"
      >
        ← All matches
      </Link>

      {state.status === 'loading' && <LoadingState label="Loading match intelligence…" />}

      {state.status === 'not-found' && (
        <ErrorState
          title="Match not found"
          message="This match doesn't exist, or the id in the URL isn't valid."
        />
      )}

      {state.status === 'error' && (
        <ErrorState title="Couldn't load this match" message={state.message} onRetry={load} />
      )}

      {state.status === 'ready' && (
        <div className="space-y-4">
          <MatchHeader match={state.data.match} />
          <PredictionSummary prediction={state.data.prediction} />
          <EvidenceBreakdown prediction={state.data.prediction} />
          <MatchIntelligence profile={state.data.profile} />
          <KeyFactors
            supportingEvidence={state.data.prediction.reasoning.supporting_evidence}
            homeTeam={state.data.prediction.reasoning.home_team}
            awayTeam={state.data.prediction.reasoning.away_team}
          />
          <DataStatus />
        </div>
      )}
    </div>
  )
}
