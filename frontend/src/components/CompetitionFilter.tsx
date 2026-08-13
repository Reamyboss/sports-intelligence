interface CompetitionFilterProps {
  competitions: string[]
  value: string
  onChange: (value: string) => void
}

export function CompetitionFilter({ competitions, value, onChange }: CompetitionFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor="competition-filter" className="text-sm text-[var(--text-muted)]">
        Competition
      </label>
      <select
        id="competition-filter"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      >
        <option value="all">All competitions</option>
        {competitions.map((competition) => (
          <option key={competition} value={competition}>
            {competition}
          </option>
        ))}
      </select>
    </div>
  )
}
