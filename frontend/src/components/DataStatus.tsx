import { CONTEXT_FACTORS, SCORED_FACTORS, UNAVAILABLE_FACTORS } from '../lib/factors'
import type { FactorDefinition } from '../lib/factors'

/**
 * A compact, scannable trust checklist - deliberately separate from
 * KeyFactors (which explains *why* each factor matters for this
 * specific match). This answers "what does the system actually know,
 * at all" as quickly as possible.
 *
 * The three groups are not cosmetic. A reader who cannot tell a
 * factor that moved the verdict from one that was merely displayed
 * would over-read the prediction, so the distinction is stated rather
 * than implied.
 */

const GROUPS: {
  title: string
  blurb: string
  factors: FactorDefinition[]
  tone: 'scored' | 'context' | 'absent'
  status: string
}[] = [
  {
    title: 'Used in the verdict',
    blurb: 'Real evidence, weighed by the engine.',
    factors: SCORED_FACTORS,
    tone: 'scored',
    status: 'Scored',
  },
  {
    title: 'Shown, but not scored',
    blurb: 'Real and computed the same safe way - presented for you to judge, not weighed by the engine.',
    factors: CONTEXT_FACTORS,
    tone: 'context',
    status: 'Context',
  },
  {
    title: 'Not available',
    blurb: 'No data source exists for these, so the engine never sees them.',
    factors: UNAVAILABLE_FACTORS,
    tone: 'absent',
    status: 'Unavailable',
  },
]

const TONE: Record<'scored' | 'context' | 'absent', string> = {
  scored: 'text-[var(--home)]',
  context: 'text-[var(--text)]',
  absent: 'text-[var(--text-muted)]',
}

export function DataStatus() {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <h2 className="text-base font-semibold text-[var(--text)]">Data status</h2>
      <p className="mt-0.5 text-sm text-[var(--text-muted)]">
        What this prediction is - and isn&apos;t - built on.
      </p>

      <div className="mt-5 space-y-5">
        {GROUPS.map((group) => (
          <div key={group.title}>
            <h3 className="text-sm font-semibold text-[var(--text)]">{group.title}</h3>
            <p className="mt-0.5 text-xs leading-relaxed text-[var(--text-muted)]">
              {group.blurb}
            </p>

            <dl className="mt-2.5 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
              {group.factors.map((factor) => (
                <div
                  key={factor.key}
                  className="flex items-baseline justify-between gap-3 text-sm"
                >
                  <dt className="text-[var(--text)]">
                    {factor.label}
                    {factor.note && (
                      <span className="mt-0.5 block text-xs text-[var(--text-muted)]">
                        {factor.note}
                      </span>
                    )}
                  </dt>
                  <dd className={`shrink-0 font-medium ${TONE[group.tone]}`}>
                    {group.status}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        ))}
      </div>
    </section>
  )
}
