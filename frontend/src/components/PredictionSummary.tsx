import type { PredictionResult } from '../api/types'
import { ConfidenceMeter } from './ConfidenceMeter'

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
      <h2 className="text-base font-semibold text-[var(--text)]">Prediction</h2>

      <div className="mt-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="text-2xl font-semibold text-[var(--text)] sm:text-3xl">
          {isDraw ? 'Draw' : favoured}
        </span>
        <span className="text-lg font-medium text-[var(--text-muted)] tabular-nums">
          {prediction.probability.toFixed(0)}% probability
        </span>
      </div>
      <p className="mt-1 text-xs text-[var(--text-muted)]">
        A probability, not a guarantee - see the confidence below for how consistent the
        supporting evidence is.
      </p>

      <p className="mt-4 text-sm leading-relaxed text-[var(--text)]">{prediction.summary}</p>

      <div className="mt-5 max-w-sm">
        <ConfidenceMeter confidence={prediction.confidence} />
      </div>

      {prediction.explanation.length > 0 && (
        <div className="mt-5 border-t border-[var(--accent)]/20 pt-4">
          <h3 className="text-sm font-semibold text-[var(--text)]">Why</h3>
          <ul className="mt-2 space-y-1.5">
            {prediction.explanation.map((line, index) => (
              <li key={index} className="text-sm text-[var(--text-muted)]">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
