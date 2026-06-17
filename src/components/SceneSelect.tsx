import type { Scene } from '../types'

interface SceneSelectProps {
  value: Scene | null
  onChange: (v: Scene) => void
}

const OPTIONS: { value: Scene; label: string; desc: string }[] = [
  { value: 'tell-parent', label: '想告诉家长', desc: '把话变成能发给爸妈的' },
  { value: 'tell-teacher', label: '想告诉老师', desc: '把话变成能发给老师的' },
  { value: 'sort-out', label: '先理清楚', desc: '我自己还没想好怎么说' },
  { value: 'urgent', label: '情况比较紧急', desc: '我现在就需要真人帮助' },
]

export function SceneSelect({ value, onChange }: SceneSelectProps) {
  return (
    <div className="options-grid two-col">
      {OPTIONS.map((o) => (
        <button
          key={o.value}
          type="button"
          className={`option-card ${value === o.value ? 'active' : ''} ${o.value === 'urgent' ? 'urgent-option' : ''}`}
          onClick={() => onChange(o.value)}
        >
          <div className="option-label">{o.label}</div>
          <div className="option-desc">{o.desc}</div>
        </button>
      ))}
    </div>
  )
}
