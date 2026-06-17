import type { Identity } from '../types'

interface IdentitySelectProps {
  value: Identity | null
  onChange: (v: Identity) => void
}

const OPTIONS: { value: Identity; label: string; desc: string }[] = [
  { value: 'student', label: '我是学生', desc: '有些话想说但说不出口' },
  { value: 'parent', label: '我是家长', desc: '想听懂孩子那句话' },
  { value: 'teacher', label: '我是老师', desc: '想接住学生的信号' },
]

export function IdentitySelect({ value, onChange }: IdentitySelectProps) {
  return (
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
  )
}
