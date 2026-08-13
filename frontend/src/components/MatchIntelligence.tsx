import type { MatchProfile } from '../api/types'

interface MatchIntelligenceProps {
  profile: MatchProfile
}

const RESULT_STYLES: Record<string, string> = {
  W: 'bg-[var(--home-soft)] text-[var(--home)]',
  D: 'bg-[var(--border)] text-[var(--text-muted)]',
  L: 'bg-[var(--away-soft)] text-[var(--away)]',
}

function FormRow({ label, form }: { label: string; form: string[] }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="truncate text-sm text-[var(--text)]">{label}</span>
      <div className="flex gap-1">
        {form.length === 0 && <span className="text-xs text-[var(--text-muted)]">No data</span>}
        {form.map((result, index) => (
          <span
            key={index}
            className={`flex h-6 w-6 items-center justify-center rounded text-xs font-semibold ${
              RESULT_STYLES[result] ?? 'bg-[var(--border)] text-[var(--text-muted)]'
            }`}
            title={result === 'W' ? 'Win' : result === 'D' ? 'Draw' : result === 'L' ? 'Loss' : result}
          >
            {result}
          </span>
        ))}
      </div>
    </div>
  )
}

export function MatchIntelligence({ profile }: MatchIntelligenceProps) {
  const { head_to_head: h2h } = profile
  const h2hTotal = h2h.home_wins + h2h.draws + h2h.away_wins

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      <h2 className="text-base font-semibold text-[var(--text)]">Match intelligence</h2>
      <p className="mt-0.5 text-sm text-[var(--text-muted)]">
        What we know about this matchup, before any interpretation.
      </p>

      <div className="mt-4 space-y-3">
        <FormRow label={profile.home_team} form={profile.home_form} />
        <FormRow label={profile.away_team} form={profile.away_form} />
      </div>

      <dl className="mt-5 grid grid-cols-2 gap-4 border-t border-[var(--border)] pt-4 sm:grid-cols-3">
        <div>
          <dt className="text-xs text-[var(--text-muted)]">Home advantage</dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--text)]">
            {profile.home_advantage ? 'Yes' : 'No'}
          </dd>
        </div>
        <div>
          <dt className="text-xs text-[var(--text-muted)]">Rest days</dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--text)]">
            {profile.rest_days_home === null && profile.rest_days_away === null
              ? 'Unavailable'
              : `${profile.rest_days_home ?? '—'} / ${profile.rest_days_away ?? '—'}`}
          </dd>
        </div>
        <div>
          <dt className="text-xs text-[var(--text-muted)]">Head-to-head</dt>
          <dd className="mt-0.5 text-sm font-medium text-[var(--text)]">
            {h2hTotal === 0
              ? 'No history'
              : `${h2h.home_wins}W – ${h2h.draws}D – ${h2h.away_wins}L`}
          </dd>
        </div>
      </dl>
    </section>
  )
}
