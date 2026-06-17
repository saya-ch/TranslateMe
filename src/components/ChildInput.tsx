import { useState } from 'react'
import { CHILD_EXAMPLES } from '../data/examples'

interface ChildInputProps {
  onSubmit: (text: string) => void
}

export function ChildInput({ onSubmit }: ChildInputProps) {
  const [value, setValue] = useState('')
  const canSubmit = value.trim().length > 0

  return (
    <div className="input-panel">
      <p className="panel-hint">
        在这里写下一句话。默认只有你自己能看到，不会自动发给任何人。
      </p>
      <textarea
        className="input-box"
        placeholder="比如：我很烦，不想去学校 / 最近上课总想哭 / 爸妈只会说我矫情"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        rows={4}
        maxLength={200}
        aria-label="说一句你现在最想说的话"
      />
      <div className="input-meta">
        <span>{value.length}/200</span>
      </div>

      <div className="examples">
        <div className="examples-title">不知道怎么说？点一下试试：</div>
        <div className="examples-list">
          {CHILD_EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              className="example-chip"
              onClick={() => setValue(ex.text)}
            >
              {ex.text}
            </button>
          ))}
        </div>
      </div>

      <button
        type="button"
        className="primary-btn"
        disabled={!canSubmit}
        onClick={() => onSubmit(value)}
      >
        帮我整理
      </button>
    </div>
  )
}
