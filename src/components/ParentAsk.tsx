import { useState } from 'react'
import { PARENT_EXAMPLES } from '../data/examples'

interface ParentAskProps {
  onAsk: (question: string) => void
  onBack: () => void
}

export function ParentAsk({ onAsk, onBack }: ParentAskProps) {
  const [value, setValue] = useState('')

  return (
    <div className="input-panel">
      <p className="panel-hint">
        你可以问 AI 怎么跟孩子沟通。AI 不会透露孩子没有允许分享的内容，只会给你通用建议。
      </p>

      <textarea
        className="input-box"
        placeholder="比如：孩子最近为什么闷闷不乐？我该怎么开口？"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        rows={4}
        maxLength={200}
      />

      <div className="examples">
        <div className="examples-title">不知道怎么问？点一下试试：</div>
        <div className="examples-list">
          {PARENT_EXAMPLES.map((ex, i) => (
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

      <div className="btn-row">
        <button type="button" className="ghost-btn" onClick={onBack}>
          返回
        </button>
        <button
          type="button"
          className="primary-btn"
          disabled={!value.trim()}
          onClick={() => onAsk(value)}
        >
          问问 AI
        </button>
      </div>
    </div>
  )
}
