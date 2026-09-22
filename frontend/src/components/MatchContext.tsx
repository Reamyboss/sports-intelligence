import type { ContextSignal, PredictionResult } from '../api/types'

interface MatchContextProps {
  prediction: PredictionResult
}

/**
 * Real, computed match context that the engine does not score.
 *
 * Every value here is built under the same before-kickoff boundary as
 * the scored evidence, so nothing leaks from the future. What makes
 * it different is that it carries no weight: placing it beside a
 * verdict without saying so would let a reader assume a heavy fixture
 * list or a league position drove the call, when neither did. The
 * heading says it outright rather than relying on the reader to infer
 * it from where the block sits on the page.
 */

function SideValue({
  team,
  value,
  favoured,
}: {
  team: string
  value: string
  favoured: boolean
}) {
  return (
    <div className="min-w-0">
      <p className="truncate text-xs text-[var(--text-muted)]">{team}</p>
      <p
        className={`mt-0.5 text-sm font-medium ${
          favoured ? 'text-[var(--home)]' : 'text-[var(--text)]'
        }`}
      >
        {value}
      </p>
    </div>
  )
}

function SignalRow({
  signal,
  homeTeam,
  awayTeam,
}: {
  signal: ContextSignal
  homeTeam: string
  awayTeam: string
}) {
  return (
    <div className="border-t border-[var(--border)] pt-4 first:border-t-0 first:pt-0">
      <h3 className="text-sm font-semibold text-[var(--text)]">{signal.title}</h3>

      <div className="mt-2 grid grid-cols-2 gap-4">
        <SideValue
          team={homeTeam}
          value={signal.home_value}
          favoured={signal.favours === 'HOME'}
        />
        <SideValue
          team={awayTeam}
          value={signal.away_value}
          favoured={signal.favours === 'AWAY'}
        />
      </div>

      <p className="mt-2 text-xs leading-relaxed text-[var(--text-muted)]">{signal.detail}</p>
    </div>
  )
}

export function MatchContext({ prediction }: MatchContextProps) {
  const signals = prediction.context

  // Nothing to show is a real outcome, not an error: a competition
  // with no table and a team with no recent fixtures both legitimately
  // produce no context at all. Rendering an empty shell would imply
  // something failed.
  if (signals.length === 0) {
    return null
  }

  const { home_team: homeTeam, away_team: awayTeam } = prediction.reasoning

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <h2 className="text-base font-semibold text-[var(--text)]">Context (not scored)</h2>
      <p className="mt-0.5 text-sm text-[var(--text-muted)]">
        Real and computed the same safe way as the evidence above &mdash; but the engine does
        not weigh any of it. Read it yourself; it did not move the verdict.
      </p>

      <div className="mt-4 space-y-4">
        {signals.map((signal) => (
          <SignalRow
            key={signal.title}
            signal={signal}
            homeTeam={homeTeam}
            awayTeam={awayTeam}
          />
        ))}
      </div>
    </section>
  )
}
