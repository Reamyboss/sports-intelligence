/**
 * Honest positioning for the prediction layer.
 *
 * Measured on 20,632 completed matches (backend/scripts/run_backtest.py,
 * re-run after the football-data.co.uk historical expansion) under
 * strict temporal safety, the engine picks the right outcome 46.9% of
 * the time. Always picking the home team scores 44.1% on those same
 * matches. That is a measured edge in this specific backtest, not a
 * proven one - it comes from one dataset and one point in time, not
 * forward/live testing, and is not a claim this will hold in the
 * future. Framed conservatively on purpose; do not strengthen this
 * wording without a stronger result to back it.
 *
 * The numbers here are hardcoded deliberately: they are a verified
 * result from a specific, reproducible backtest, not a live metric.
 * Update them only when that backtest is re-run.
 */

const ENGINE_ACCURACY = '46.9%'
const HOME_BASELINE = '44.1%'
const SAMPLE = '20,632'

export function PredictionCaveat() {
  return (
    <section className="rounded-xl border border-[var(--warn)]/30 bg-[var(--warn-soft)] p-4 sm:p-5">
      <h2 className="text-sm font-semibold text-[var(--warn)]">
        Read this as evidence, not as a tip
      </h2>

      <p className="mt-2 text-sm leading-relaxed text-[var(--text)]">
        This engine is experimental. In a backtest against {SAMPLE} completed matches, it picked
        the right outcome <strong>{ENGINE_ACCURACY}</strong> of the time, against{' '}
        <strong>{HOME_BASELINE}</strong> for simply always backing the home team &mdash; a
        measured edge in this backtest, not a proven or guaranteed one going forward.
      </p>

      <p className="mt-2 text-sm leading-relaxed text-[var(--text-muted)]">
        What the system is genuinely good at is showing you the real reasoning behind a match and
        where the evidence disagrees with itself &mdash; draw your own conclusion from that, not
        from the percentage alone.
      </p>
    </section>
  )
}
