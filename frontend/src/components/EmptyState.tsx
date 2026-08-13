interface EmptyStateProps {
  title: string
  message?: string
}

export function EmptyState({ title, message }: EmptyStateProps) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-2 rounded-xl border border-dashed border-[var(--border)] px-6 py-16 text-center">
      <p className="text-sm font-medium text-[var(--text)]">{title}</p>
      {message && <p className="text-sm text-[var(--text-muted)]">{message}</p>}
    </div>
  )
}
