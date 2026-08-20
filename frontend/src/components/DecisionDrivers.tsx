import type { ConflictLevel, Evidence, PredictionResult } from '../api/types'

interface DecisionDriversProps {
  prediction: PredictionResult
}

const CONFLICT_COPY: Record<ConflictLevel, { label: string; note: string; tone: string }> = {
  NONE: {
    label: 'Evidence agrees',
    note: 'Every signal points the same way.',
    tone: 'text-[var(--home)] bg-[var(--home-soft)]',
  },
  LOW: {
    label: 'Mostly agrees',
    note: 'One side is clearly stronger; the counter-signal is minor.',
    tone: 'text-[var(--home)] bg-[var(--home-soft)]',
  },
  MODERATE: {
    label: 'Mixed evidence',
    note: 'There is a real case on both sides.',
    tone: 'text-[var(--warn)] bg-[var(--warn-soft)]',
  },
  HIGH: {
    label: 'Evidence is split',
    note: 'Both sides are close to equally strong - this call could go the other way.',
    tone: 'text-[var(--away)] bg-[var(--away-soft)]',
  },
}

function Signal({
  heading,
  evidence,
  team,
  accent,
  emptyLabel,
}: {
  heading: string
  evidence: Evidence | null
  team: string
  accent: string
  emptyLabel: string
}) {
  return (
    <div className="flex-1 rounded-lg border border-[var(--border)] p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wide" style={{ color: accent }}>
        {heading}
      </h3>

      {evidence ? (
        <>
          <p className="mt-2 text-sm font-medium text-[var(--text)]">{evidence.title}</p>
          <p className="mt-1 text-sm text-[var(--text-muted)]">{evidence.reason}</p>
          <p className="mt-2 text-xs text-[var(--text-muted)]">Favours {team}</p>
        </>
      ) : (
        <p className="mt-2 text-sm text-[var(--text-muted)]">{emptyLabel}</p>
      )}
    </div>
  )
}

/**
 * The single strongest signal for the call and the single strongest
 * one against it, chosen by the magnitude the engine computed - not
 * by the order the rules happen to run in.
 */
export function DecisionDrivers({ prediction }: DecisionDriversProps) {
  const { reasoning, strongest_support, strongest_opposition, conflict } = prediction

  const teamFor = (evidence: Evidence | null) =>
    evidence?.supports === 'HOME' ? reasoning.home_team : reasoning.away_team

  const conflictCopy = CONFLICT_COPY[conflict] ?? CONFLICT_COPY.NONE

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-[var(--text)]">Why</h2>
          <p className="mt-0.5 text-sm text-[var(--text-muted)]">
            The strongest evidence for this call, and the strongest against it.
          </p>
        </div>

        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${conflictCopy.tone}`}
        >
          {conflictCopy.label}
        </span>
      </div>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <Signal
          heading="Strongest support"
          evidence={strongest_support}
          team={teamFor(strongest_support)}
          accent="var(--home)"
          emptyLabel="No single standout signal - this call rests on the weight of several smaller ones."
        />
        <Signal
          heading="Strongest opposition"
          evidence={strongest_opposition}
          team={teamFor(strongest_opposition)}
          accent="var(--away)"
          emptyLabel="Nothing in the evidence argues against this call."
        />
      </div>

      <p className="mt-3 text-sm text-[var(--text-muted)]">{conflictCopy.note}</p>
    </section>
  )
}
