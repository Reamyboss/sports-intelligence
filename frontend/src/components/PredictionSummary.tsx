import type { PredictionResult } from '../api/types'
import { ConfidenceMeter } from './ConfidenceMeter'
import { ProbabilityBar } from './ProbabilityBar'

interface PredictionSummaryProps {
  prediction: PredictionResult
}

function favouredLabel(prediction: PredictionResult): string {
  const { winner, reasoning } = prediction

  if (winner === 'HOME') return reasoning.home_team
  if (winner === 'AWAY') return reasoning.away_team
  return 'Draw'
}

export function PredictionSummary({ prediction }: PredictionSummaryProps) {
  const favoured = favouredLabel(prediction)
  const isDraw = prediction.winner === 'DRAW'

  return (
    <section className="rounded-xl border border-[var(--accent)]/30 bg-[var(--accent-soft)] p-5 sm:p-6">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)]">
        What we think
      </h2>

      <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="text-2xl font-semibold text-[var(--text)] sm:text-3xl">
          {isDraw ? 'Draw' : favoured}
        </span>
        <span className="text-lg font-medium text-[var(--text-muted)] tabular-nums">
          {prediction.probability.toFixed(0)}%
        </span>
      </div>

      <p className="mt-1 text-xs text-[var(--text-muted)]">
        {isDraw
          ? 'The most likely single outcome, not a certainty.'
          : `The chance of ${favoured} winning - not of the match being close.`}
      </p>

      <div className="mt-5">
        <ProbabilityBar prediction={prediction} />
      </div>

      <p className="mt-5 text-sm leading-relaxed text-[var(--text)]">{prediction.summary}</p>

      <div className="mt-5 max-w-sm">
        <ConfidenceMeter confidence={prediction.confidence} />
      </div>
    </section>
  )
}
