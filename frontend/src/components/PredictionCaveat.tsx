/**
 * Honest positioning for the prediction layer.
 *
 * Measured on 3,489 completed matches under strict temporal safety,
 * the engine picks the right outcome 42.9% of the time. Always
 * picking the home team scores 44.5% on the same matches. The engine
 * does not currently beat that baseline, and the product must not
 * imply otherwise.
 *
 * The numbers here are hardcoded deliberately: they are a verified
 * result from a specific, reproducible backtest, not a live metric.
 * Update them only when that backtest is re-run.
 */

const ENGINE_ACCURACY = '42.9%'
const HOME_BASELINE = '44.5%'
const SAMPLE = '3,489'

export function PredictionCaveat() {
  return (
    <section className="rounded-xl border border-[var(--warn)]/30 bg-[var(--warn-soft)] p-4 sm:p-5">
      <h2 className="text-sm font-semibold text-[var(--warn)]">
        Read this as evidence, not as a tip
      </h2>

      <p className="mt-2 text-sm leading-relaxed text-[var(--text)]">
        This engine is experimental. Tested against {SAMPLE} completed matches, it picked the
        right outcome <strong>{ENGINE_ACCURACY}</strong> of the time. Simply always backing the
        home team would have scored <strong>{HOME_BASELINE}</strong> on those same matches.
      </p>

      <p className="mt-2 text-sm leading-relaxed text-[var(--text-muted)]">
        So the verdict above is not a proven edge. What the system is genuinely good at is
        showing you the real evidence behind a match and where that evidence disagrees with
        itself &mdash; use that, and draw your own conclusion.
      </p>
    </section>
  )
}
