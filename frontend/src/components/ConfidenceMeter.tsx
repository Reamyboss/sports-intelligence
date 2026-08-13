interface ConfidenceMeterProps {
  confidence: number
}

function levelFor(confidence: number): { label: string; color: string } {
  if (confidence >= 70) return { label: 'High confidence', color: 'var(--home)' }
  if (confidence >= 45) return { label: 'Moderate confidence', color: 'var(--warn)' }
  return { label: 'Low confidence', color: 'var(--away)' }
}

export function ConfidenceMeter({ confidence }: ConfidenceMeterProps) {
  const clamped = Math.min(100, Math.max(0, confidence))
  const { label, color } = levelFor(clamped)

  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-[var(--text)]">{label}</span>
        <span className="tabular-nums text-[var(--text-muted)]">{clamped.toFixed(0)}%</span>
      </div>
      <div
        role="meter"
        aria-valuenow={Math.round(clamped)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Prediction confidence"
        className="mt-2 h-2 w-full overflow-hidden rounded-full bg-[var(--border)]"
      >
        <div
          className="h-full rounded-full transition-[width]"
          style={{ width: `${clamped}%`, backgroundColor: color }}
        />
      </div>
      <p className="mt-1.5 text-xs text-[var(--text-muted)]">
        Confidence reflects how consistent the evidence is - not how likely the predicted outcome
        is.
      </p>
    </div>
  )
}
