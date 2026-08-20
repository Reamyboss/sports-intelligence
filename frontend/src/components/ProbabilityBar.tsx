import type { PredictionResult } from '../api/types'

interface ProbabilityBarProps {
  prediction: PredictionResult
}

interface Outcome {
  key: 'HOME' | 'DRAW' | 'AWAY'
  label: string
  value: number
  color: string
}

/**
 * All three outcomes, always. A single percentage next to one team
 * can't say whether the other 60% is a draw or the opponent winning -
 * and when that number was the home team's chance printed beside the
 * away team's name, it said something actively false.
 */
export function ProbabilityBar({ prediction }: ProbabilityBarProps) {
  const { reasoning } = prediction

  const outcomes: Outcome[] = [
    {
      key: 'HOME',
      label: reasoning.home_team,
      value: prediction.home_probability,
      color: 'var(--home)',
    },
    { key: 'DRAW', label: 'Draw', value: prediction.draw_probability, color: 'var(--text-muted)' },
    {
      key: 'AWAY',
      label: reasoning.away_team,
      value: prediction.away_probability,
      color: 'var(--away)',
    },
  ]

  return (
    <div>
      <div
        className="flex h-2.5 w-full overflow-hidden rounded-full bg-[var(--border)]"
        role="img"
        aria-label={outcomes
          .map((outcome) => `${outcome.label} ${outcome.value.toFixed(0)}%`)
          .join(', ')}
      >
        {outcomes.map((outcome) => (
          <div
            key={outcome.key}
            className="h-full first:rounded-l-full last:rounded-r-full"
            style={{ width: `${outcome.value}%`, backgroundColor: outcome.color }}
          />
        ))}
      </div>

      <dl className="mt-3 grid grid-cols-3 gap-2 sm:gap-3">
        {outcomes.map((outcome) => {
          const isPredicted = outcome.key === prediction.winner

          return (
            <div
              key={outcome.key}
              className={`min-w-0 rounded-lg border px-2.5 py-2 sm:px-3 ${
                isPredicted
                  ? 'border-[var(--accent)]/40 bg-[var(--accent-soft)]'
                  : 'border-transparent bg-[var(--bg)]'
              }`}
            >
              <dt className="flex items-center gap-1.5">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ backgroundColor: outcome.color }}
                  aria-hidden="true"
                />
                <span className="truncate text-xs text-[var(--text-muted)]">{outcome.label}</span>
              </dt>
              <dd
                className={`mt-0.5 tabular-nums ${
                  isPredicted
                    ? 'text-lg font-semibold text-[var(--text)]'
                    : 'text-base font-medium text-[var(--text-muted)]'
                }`}
              >
                {outcome.value.toFixed(0)}%
              </dd>
            </div>
          )
        })}
      </dl>
    </div>
  )
}
