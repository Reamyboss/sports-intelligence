/**
 * The honest, verified list of match-intelligence factor categories.
 *
 * `available: true` means a real backend evidence source exists for
 * it (app/evidence/*.py, reused unmodified here - nothing is
 * recomputed in the frontend). `available: false` means no data
 * pipeline is connected - confirmed against app/collectors/ and
 * app/providers/, which only fetch fixtures, results, and team
 * rosters. Do not flip a category to available unless a real backend
 * source for it exists.
 */

export interface FactorDefinition {
  /** Matches Evidence.title from the backend exactly, for the available ones. */
  key: string
  label: string
  available: boolean
  note?: string
}

export const SCORED_FACTORS: FactorDefinition[] = [
  { key: 'Recent Form', label: 'Recent form' },
  { key: 'Goals Scored', label: 'Goals scored' },
  { key: 'Home/Away Record', label: 'Home/away record' },
  { key: 'Current Streak', label: 'Current streak' },
  { key: 'Head-to-Head', label: 'Head-to-head history' },
].map((f) => ({ ...f, available: true }))

export const UNAVAILABLE_FACTORS: FactorDefinition[] = [
  {
    key: 'Rest',
    label: 'Rest days',
    available: false,
    note: 'Shown in match intelligence above - real, but not yet factored into the prediction itself.',
  },
  { key: 'Travel', label: 'Travel distance', available: false },
  { key: 'Fatigue', label: 'Fixture congestion / fatigue', available: false },
  { key: 'Weather', label: 'Weather', available: false },
  { key: 'Pitch', label: 'Pitch conditions', available: false },
  { key: 'Injuries', label: 'Verified injuries', available: false },
  { key: 'Lineup', label: 'Confirmed lineups', available: false },
  { key: 'Live', label: 'Live match state', available: false },
  { key: 'CompetitionContext', label: 'Competition context (standings, stakes)', available: false },
]

export const ALL_FACTORS: FactorDefinition[] = [...SCORED_FACTORS, ...UNAVAILABLE_FACTORS]
