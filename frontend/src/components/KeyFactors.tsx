import type { Evidence } from '../api/types'
import { SCORED_FACTORS, UNAVAILABLE_FACTORS } from '../lib/factors'

interface KeyFactorsProps {
  supportingEvidence: Evidence[]
  homeTeam: string
  awayTeam: string
}

export function KeyFactors({ supportingEvidence, homeTeam, awayTeam }: KeyFactorsProps) {
  const byTitle = new Map(supportingEvidence.map((item) => [item.title, item]))

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <h2 className="text-base font-semibold text-[var(--text)]">Key factors</h2>
      <p className="mt-0.5 text-sm text-[var(--text-muted)]">
        Every category the system can actually evaluate for this match - and, just as
        importantly, the ones it can't yet.
      </p>

      <ul className="mt-4 divide-y divide-[var(--border)]">
        {SCORED_FACTORS.map((factor) => {
          const evidence = byTitle.get(factor.key)

          return (
            <li key={factor.key} className="flex items-start justify-between gap-4 py-3">
              <div>
                <p className="text-sm font-medium text-[var(--text)]">{factor.label}</p>
                <p className="mt-0.5 text-sm text-[var(--text-muted)]">
                  {evidence
                    ? `${evidence.reason} (favors ${evidence.supports === 'HOME' ? homeTeam : awayTeam})`
                    : 'No notable signal for this match.'}
                </p>
              </div>
              <span className="mt-0.5 shrink-0 rounded-full bg-[var(--home-soft)] px-2 py-0.5 text-xs font-medium text-[var(--home)]">
                Available
              </span>
            </li>
          )
        })}

        {UNAVAILABLE_FACTORS.map((factor) => (
          <li key={factor.key} className="flex items-start justify-between gap-4 py-3">
            <div>
              <p className="text-sm font-medium text-[var(--text-muted)]">{factor.label}</p>
              {factor.note && (
                <p className="mt-0.5 text-sm text-[var(--text-muted)]">{factor.note}</p>
              )}
            </div>
            <span className="mt-0.5 shrink-0 rounded-full bg-[var(--border)] px-2 py-0.5 text-xs font-medium text-[var(--text-muted)]">
              Unavailable
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
