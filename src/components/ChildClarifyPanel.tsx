import { useState } from 'react'
import type { ChildClarify } from '../types'

interface ChildClarifyPanelProps {
  initial: ChildClarify
  onConfirm: (clarify: ChildClarify) => void
  onBack: () => void
}

export function ChildClarifyPanel({ initial, onConfirm, onBack }: ChildClarifyPanelProps) {
  const [clarify, setClarify] = useState<ChildClarify>(initial)

  const update = (key: keyof ChildClarify, value: string) => {
    setClarify((c) => ({ ...c, [key]: value }))
  }

  return (
    <div className="clarify-panel">
      <p className="panel-hint">
        AI 帮你把刚才那句话整理成三个问题。你可以随便改，这些内容只有你自己能看到。
      </p>

      <div className="clarify-block">
        <label className="block-label">我真正想表达什么</label>
        <textarea
          className="input-box"
          value={clarify.wantToSay}
          onChange={(e) => update('wantToSay', e.target.value)}
          rows={3}
          maxLength={200}
        />
      </div>

      <div className="clarify-block">
        <label className="block-label">我怕什么</label>
        <textarea
          className="input-box"
          value={clarify.fear}
          onChange={(e) => update('fear', e.target.value)}
          rows={3}
          maxLength={200}
        />
      </div>

      <div className="clarify-block">
        <label className="block-label">我希望大人怎么做</label>
        <textarea
          className="input-box"
          value={clarify.hope}
          onChange={(e) => update('hope', e.target.value)}
          rows={3}
          maxLength={200}
        />
      </div>

      <div className="btn-row">
        <button type="button" className="ghost-btn" onClick={onBack}>
          返回
        </button>
        <button
          type="button"
          className="primary-btn"
          onClick={() => onConfirm(clarify)}
        >
          下一步：选择分享范围
        </button>
      </div>
    </div>
  )
}
