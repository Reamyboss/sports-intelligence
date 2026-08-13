import type { Evidence, PredictionResult } from '../api/types'

interface EvidenceBreakdownProps {
  prediction: PredictionResult
}

function EvidenceList({ items, emptyLabel }: { items: Evidence[]; emptyLabel: string }) {
  if (items.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">{emptyLabel}</p>
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li key={index} className="flex items-start gap-2 text-sm text-[var(--text)]">
          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
          <span>{item.reason}</span>
        </li>
      ))}
    </ul>
  )
}

export function EvidenceBreakdown({ prediction }: EvidenceBreakdownProps) {
  const { reasoning, winner } = prediction
  const evidence = reasoning.supporting_evidence

  const isDecisive = winner === 'HOME' || winner === 'AWAY'
  const favouredSide = winner === 'HOME' ? 'HOME' : 'AWAY'
  const favouredTeam = winner === 'HOME' ? reasoning.home_team : reasoning.away_team
  const otherTeam = winner === 'HOME' ? reasoning.away_team : reasoning.home_team

  const supporting = isDecisive ? evidence.filter((item) => item.supports === favouredSide) : []
  const counter = isDecisive ? evidence.filter((item) => item.supports !== favouredSide) : []

  const homeEvidence = evidence.filter((item) => item.supports === 'HOME')
  const awayEvidence = evidence.filter((item) => item.supports === 'AWAY')

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
      {isDecisive ? (
        <>
          <h2 className="text-base font-semibold text-[var(--text)]">
            Why the engine favors {favouredTeam}
          </h2>
          <p className="mt-0.5 text-sm text-[var(--text-muted)]">
            The strongest real evidence behind this prediction.
          </p>
          <div className="mt-3 text-[var(--home)]">
            <EvidenceList items={supporting} emptyLabel="No strong supporting signal found - this prediction leans on the evidence-weighted count alone." />
          </div>

          <h3 className="mt-5 text-sm font-semibold text-[var(--warn)]">Counter signals</h3>
          <p className="mt-0.5 text-sm text-[var(--text-muted)]">
            What points the other way, for {otherTeam}.
          </p>
          <div className="mt-3 text-[var(--warn)]">
            <EvidenceList items={counter} emptyLabel="No real evidence found against this prediction." />
          </div>
        </>
      ) : (
        <>
          <h2 className="text-base font-semibold text-[var(--text)]">Evidence &amp; reasoning</h2>
          <p className="mt-0.5 text-sm text-[var(--text-muted)]">
            The evidence is genuinely contested - here's what each side has.
          </p>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <div className="flex-1 rounded-lg border border-[var(--border)] p-4">
              <h3 className="text-sm font-semibold text-[var(--home)]">
                Favors {reasoning.home_team}
              </h3>
              <div className="mt-3 text-[var(--home)]">
                <EvidenceList items={homeEvidence} emptyLabel="No supporting evidence found." />
              </div>
            </div>
            <div className="flex-1 rounded-lg border border-[var(--border)] p-4">
              <h3 className="text-sm font-semibold text-[var(--away)]">
                Favors {reasoning.away_team}
              </h3>
              <div className="mt-3 text-[var(--away)]">
                <EvidenceList items={awayEvidence} emptyLabel="No supporting evidence found." />
              </div>
            </div>
          </div>
        </>
      )}

      {reasoning.contradictions.length > 0 && (
        <div className="mt-4 rounded-lg border border-[var(--warn)]/30 bg-[var(--warn-soft)] p-4">
          <h3 className="text-sm font-semibold text-[var(--warn)]">Contradictions &amp; uncertainty</h3>
          <ul className="mt-2 space-y-1.5">
            {reasoning.contradictions.map((text, index) => (
              <li key={index} className="text-sm text-[var(--text)]">
                {text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
