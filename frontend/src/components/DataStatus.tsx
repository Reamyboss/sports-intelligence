import { ALL_FACTORS } from '../lib/factors'

/**
 * A compact, scannable trust checklist - deliberately separate from
 * KeyFactors (which explains *why* each available factor matters for
 * this specific match). This just answers "what does the system
 * actually know, at all" as quickly as possible.
 */
export function DataStatus() {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <h2 className="text-base font-semibold text-[var(--text)]">Data status</h2>
      <p className="mt-0.5 text-sm text-[var(--text-muted)]">
        What this prediction is - and isn't - built on.
      </p>

      <dl className="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
        {ALL_FACTORS.map((factor) => (
          <div key={factor.key} className="flex items-center justify-between gap-3 text-sm">
            <dt className="text-[var(--text)]">{factor.label}</dt>
            <dd
              className={`shrink-0 font-medium ${
                factor.available ? 'text-[var(--home)]' : 'text-[var(--text-muted)]'
              }`}
            >
              {factor.available ? 'Available' : 'Unavailable'}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
