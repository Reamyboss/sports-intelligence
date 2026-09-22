/**
 * The honest, verified list of match-intelligence factor categories.
 *
 * `available: true` means a real backend source exists for it
 * (app/evidence/*.py, reused unmodified here - nothing is recomputed
 * in the frontend). `available: false` means no data pipeline is
 * connected - confirmed against app/collectors/ and app/providers/.
 * Do not flip a category to available unless a real backend source
 * for it exists.
 *
 * Two lists are available, and the split matters. SCORED_FACTORS move
 * the prediction. CONTEXT_FACTORS are just as real and just as
 * temporally safe, but are deliberately not weighed - they reach the
 * reader on PredictionResult.context and never touch the maths, so
 * the published accuracy figure still describes the running engine.
 *
 * Four categories were removed rather than left showing "Unavailable"
 * forever: pitch conditions, verified injuries, confirmed lineups and
 * live match state. No free source exists for any of them, so they
 * were permanently dead rows rather than a roadmap.
 */

export interface FactorDefinition {
  /** Matches Evidence.title / ContextSignal.title from the backend exactly. */
  key: string
  label: string
  available: boolean
  /** True when the factor is shown to the reader but not scored. */
  contextOnly?: boolean
  note?: string
}

export const SCORED_FACTORS: FactorDefinition[] = [
  { key: 'Recent Form', label: 'Recent form' },
  { key: 'Goals Scored', label: 'Goals scored' },
  { key: 'Home/Away Record', label: 'Home/away record' },
  { key: 'Current Streak', label: 'Current streak' },
  { key: 'Head-to-Head', label: 'Head-to-head history' },
  { key: 'Rest Days', label: 'Rest days' },
].map((f) => ({ ...f, available: true }))

export const CONTEXT_FACTORS: FactorDefinition[] = [
  { key: 'Fixture Congestion', label: 'Fixture congestion / fatigue' },
  { key: 'Competition Context', label: 'Competition context (standings)' },
].map((f) => ({ ...f, available: true, contextOnly: true }))

export const UNAVAILABLE_FACTORS: FactorDefinition[] = [
  {
    key: 'Travel',
    label: 'Travel distance',
    available: false,
    note: 'Needs stadium coordinates, which the current data source does not provide.',
  },
  {
    key: 'Weather',
    label: 'Weather',
    available: false,
    note: 'Depends on stadium coordinates being available first.',
  },
]

export const ALL_FACTORS: FactorDefinition[] = [
  ...SCORED_FACTORS,
  ...CONTEXT_FACTORS,
  ...UNAVAILABLE_FACTORS,
]
