import { useId, useState } from 'react'
import type { ReactNode } from 'react'

interface DisclosureProps {
  title: string
  subtitle: string
  defaultOpen?: boolean
  children: ReactNode
}

/**
 * A collapsible group header for reference material.
 *
 * Deliberately not a card: the sections it wraps already draw their
 * own, and nesting one card inside another produces a double border
 * and an ambiguous hierarchy. This renders as a labelled rule with a
 * toggle, so the cards below it read as belonging to the group
 * without being boxed twice.
 *
 * Collapsed content is unmounted rather than hidden with CSS. These
 * groups sit below the fold and hold the page's densest material, so
 * not rendering them until asked keeps the initial view cheap.
 */
export function Disclosure({ title, subtitle, defaultOpen = false, children }: DisclosureProps) {
  const [open, setOpen] = useState(defaultOpen)
  const panelId = useId()

  return (
    <section>
      <h2>
        <button
          type="button"
          onClick={() => setOpen((current) => !current)}
          aria-expanded={open}
          aria-controls={panelId}
          className="group flex w-full items-center gap-3 rounded-lg px-1 py-3 text-left transition-colors hover:bg-[var(--surface)]"
        >
          <span className="min-w-0 flex-1">
            <span className="block text-sm font-semibold text-[var(--text)]">{title}</span>
            <span className="mt-0.5 block text-xs text-[var(--text-muted)]">{subtitle}</span>
          </span>

          <span className="shrink-0 text-xs font-medium text-[var(--text-muted)]">
            {open ? 'Hide' : 'Show'}
          </span>

          <svg
            viewBox="0 0 20 20"
            fill="none"
            aria-hidden="true"
            className={`h-4 w-4 shrink-0 text-[var(--text-muted)] transition-transform ${
              open ? 'rotate-180' : ''
            }`}
          >
            <path
              d="M5 7.5 10 12.5 15 7.5"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </h2>

      {open && (
        <div id={panelId} className="mt-2 space-y-4">
          {children}
        </div>
      )}
    </section>
  )
}
