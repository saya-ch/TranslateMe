import type { ShareScope } from '../types'

interface ShareScopeSelectProps {
  value: ShareScope | null
  onChange: (v: ShareScope) => void
  onBack: () => void
}

const OPTIONS: { value: ShareScope; label: string; desc: string }[] = [
  { value: 'private', label: '只让我自己看看', desc: '不会发给任何人' },
  { value: 'self-send', label: '帮我生成一段话，我自己发', desc: '生成草稿，你自己决定怎么发' },
  { value: 'send-parent', label: '帮我发给家长', desc: '生成沟通请求，确认后发到家长端' },
  { value: 'vague', label: '只告诉家长一个很模糊的提醒', desc: '只发"孩子想跟你聊聊"，不透露具体内容' },
]

export function ShareScopeSelect({ value, onChange, onBack }: ShareScopeSelectProps) {
  return (
    <div className="scope-panel">
      <p className="panel-hint">你想怎么处理这段话？</p>

      <div className="options-grid">
        {OPTIONS.map((o) => (
          <button
            key={o.value}
            type="button"
            className={`option-card ${value === o.value ? 'active' : ''}`}
            onClick={() => onChange(o.value)}
          >
            <div className="option-label">{o.label}</div>
            <div className="option-desc">{o.desc}</div>
          </button>
        ))}
      </div>

      <button type="button" className="ghost-btn" onClick={onBack}>
        返回
      </button>
    </div>
  )
}
