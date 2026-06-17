interface QuickAction {
  key: string
  label: string
  onClick: () => void
}

interface QuickActionsProps {
  actions: QuickAction[]
  onSwitchIdentity: () => void
}

export function QuickActions({ actions, onSwitchIdentity }: QuickActionsProps) {
  const allActions = [...actions, { key: 'switch', label: '切换身份', onClick: onSwitchIdentity }]

  return (
    <div className="quick-actions">
      {allActions.map((a) => (
        <button
          key={a.key}
          type="button"
          className={`quick-action-btn ${a.key === 'switch' ? 'switch-btn' : ''}`}
          onClick={a.onClick}
        >
          {a.label}
        </button>
      ))}
    </div>
  )
}
