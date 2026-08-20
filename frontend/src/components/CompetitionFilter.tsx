import type { Competition } from '../api/types'
import { competitionLabel } from '../lib/competitions'

interface CompetitionFilterProps {
  competitions: Competition[]
  value: string
  onChange: (value: string) => void
}

export function CompetitionFilter({ competitions, value, onChange }: CompetitionFilterProps) {
  const active = competitions.filter((competition) => competition.availability === 'ACTIVE')
  const inactive = competitions.filter((competition) => competition.availability !== 'ACTIVE')

  return (
    <div className="flex flex-wrap items-center gap-2">
      <label htmlFor="competition-filter" className="text-sm text-[var(--text-muted)]">
        Competition
      </label>
      <select
        id="competition-filter"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="max-w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      >
        <option value="all">All competitions</option>

        {active.length > 0 && (
          <optgroup label="Fixtures to come">
            {active.map((competition) => (
              <option key={competition.name} value={competition.name}>
                {competitionLabel(competition.name)} ({competition.upcoming_matches})
              </option>
            ))}
          </optgroup>
        )}

        {inactive.length > 0 && (
          <optgroup label="No upcoming fixtures">
            {inactive.map((competition) => (
              <option key={competition.name} value={competition.name}>
                {competitionLabel(competition.name)}
              </option>
            ))}
          </optgroup>
        )}
      </select>
    </div>
  )
}
