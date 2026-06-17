import type { ShareScope } from '../../../types'

interface ScopeChatCardProps {
  id: string
  selected: ShareScope | null
  onSelect: (id: string, scope: ShareScope) => void
}

const OPTIONS: { value: ShareScope; label: string; desc: string }[] = [
  { value: 'private', label: '只让我自己看看', desc: '不会发给任何人' },
  { value: 'self-send', label: '帮我生成一段话，我自己发', desc: '生成草稿，你自己决定怎么发' },
  { value: 'send-parent', label: '帮我发给家长', desc: '生成沟通请求，确认后发到家长端' },
  { value: 'vague', label: '只告诉家长一个很模糊的提醒', desc: '只发"孩子想跟你聊聊"，不透露具体内容' },
]

export function ScopeChatCard({ id, selected, onSelect }: ScopeChatCardProps) {
  return (
    <div className="chat-card scope-chat-card">
      <div className="card-header">
        <span className="card-ai-tag">AI</span>
        <span className="card-title">你想怎么处理这段话？</span>
      </div>

      <div className="scope-options">
        {OPTIONS.map((o) => (
          <button
            key={o.value}
            type="button"
            className={`scope-option ${selected === o.value ? 'active' : ''}`}
            onClick={() => onSelect(id, o.value)}
            disabled={selected !== null}
          >
            <div className="scope-label">{o.label}</div>
            <div className="scope-desc">{o.desc}</div>
          </button>
        ))}
      </div>

      {selected && <div className="card-done-tag">已选择</div>}
    </div>
  )
}
