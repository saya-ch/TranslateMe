import { useState } from 'react'
import type { ParentMessageDraft, ShareScope } from '../types'
import { CopyButton } from './CopyButton'

interface DraftPreviewProps {
  draft: ParentMessageDraft
  scope: ShareScope
  onConfirm: (editedDraft: ParentMessageDraft) => void
  onBack: () => void
}

export function DraftPreview({ draft, scope, onConfirm, onBack }: DraftPreviewProps) {
  const [edited, setEdited] = useState<ParentMessageDraft>(draft)
  const willSend = scope === 'send-parent' || scope === 'vague'

  return (
    <div className="draft-panel">
      <p className="panel-hint">
        这是帮你整理的草稿，你可以随便改。
        {willSend ? ' 确认后会发送到家长端。' : ' 这份草稿不会自动发送。'}
      </p>

      {scope === 'vague' && (
        <div className="vague-note">
          模糊提醒模式：家长只会看到"孩子想跟你聊聊"，看不到你具体说了什么。
        </div>
      )}

      <div className="draft-card">
        <div className="draft-head">
          <span className="draft-title-label">标题</span>
          <CopyButton text={`${edited.title}\n\n${edited.body}`} />
        </div>
        <input
          className="draft-title-input"
          value={edited.title}
          onChange={(e) => setEdited({ ...edited, title: e.target.value })}
        />

        <div className="draft-body-label">内容</div>
        <textarea
          className="input-box draft-body"
          value={edited.body}
          onChange={(e) => setEdited({ ...edited, body: e.target.value })}
          rows={8}
        />
      </div>

      <div className="btn-row">
        <button type="button" className="ghost-btn" onClick={onBack}>
          返回修改
        </button>
        <button
          type="button"
          className="primary-btn"
          onClick={() => onConfirm(edited)}
        >
          {willSend ? '确认发送到家长端' : '确认保存草稿'}
        </button>
      </div>
    </div>
  )
}
