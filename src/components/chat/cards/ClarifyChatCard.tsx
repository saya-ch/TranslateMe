import { useState } from 'react'
import type { ChildClarify } from '../../../types'

interface ClarifyChatCardProps {
  id: string
  clarify: ChildClarify
  confirmed: boolean
  onConfirm: (id: string, clarify: ChildClarify) => void
  onBack: (id: string) => void
}

export function ClarifyChatCard({
  id,
  clarify,
  confirmed,
  onConfirm,
  onBack,
}: ClarifyChatCardProps) {
  const [draft, setDraft] = useState<ChildClarify>(clarify)

  const update = (key: keyof ChildClarify, value: string) => {
    setDraft((c) => ({ ...c, [key]: value }))
  }

  return (
    <div className="chat-card clarify-chat-card">
      <div className="card-header">
        <span className="card-ai-tag">AI</span>
        <span className="card-title">我帮你整理成三个问题，你可以随便改</span>
      </div>
      <p className="card-hint">这些内容只有你自己能看到，不会自动发给任何人。</p>

      <div className="clarify-block">
        <label className="block-label">我真正想表达什么</label>
        <textarea
          className="card-input"
          value={draft.wantToSay}
          onChange={(e) => update('wantToSay', e.target.value)}
          rows={3}
          maxLength={200}
          disabled={confirmed}
        />
      </div>

      <div className="clarify-block">
        <label className="block-label">我怕什么</label>
        <textarea
          className="card-input"
          value={draft.fear}
          onChange={(e) => update('fear', e.target.value)}
          rows={3}
          maxLength={200}
          disabled={confirmed}
        />
      </div>

      <div className="clarify-block">
        <label className="block-label">我希望大人怎么做</label>
        <textarea
          className="card-input"
          value={draft.hope}
          onChange={(e) => update('hope', e.target.value)}
          rows={3}
          maxLength={200}
          disabled={confirmed}
        />
      </div>

      {!confirmed && (
        <div className="card-btn-row">
          <button type="button" className="card-ghost-btn" onClick={() => onBack(id)}>
            返回
          </button>
          <button
            type="button"
            className="card-primary-btn"
            onClick={() => onConfirm(id, draft)}
          >
            确认整理
          </button>
        </div>
      )}
      {confirmed && <div className="card-done-tag">已确认</div>}
    </div>
  )
}
