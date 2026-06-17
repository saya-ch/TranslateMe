import { EXAMPLES } from '../data/examples'

interface InputPanelProps {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
}

export function InputPanel({ value, onChange, onSubmit }: InputPanelProps) {
  const canSubmit = value.trim().length > 0

  return (
    <div className="input-panel">
      <textarea
        className="input-box"
        placeholder="比如：我很烦，不想去学校 / 最近上课总想哭 / 爸妈只会说我矫情"
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              className="example-chip"
              onClick={() => onChange(ex.text)}
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
        onClick={onSubmit}
      >
        帮我说出口
      </button>
    </div>
  )
}
