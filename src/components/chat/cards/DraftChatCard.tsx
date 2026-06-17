import { useState } from 'react'
import type { ParentMessageDraft, ShareScope } from '../../../types'
import { CopyButton } from '../../CopyButton'

interface DraftChatCardProps {
  id: string
  draft: ParentMessageDraft
  scope: ShareScope
  sent: boolean
  onChange: (id: string, title: string, body: string) => void
  onSend: (id: string, title: string, body: string, isVague: boolean) => void
}

export function DraftChatCard({
  id,
  draft,
  scope,
  sent,
  onChange,
  onSend,
}: DraftChatCardProps) {
  const [title, setTitle] = useState(draft.title)
  const [body, setBody] = useState(draft.body)
  const willSend = scope === 'send-parent' || scope === 'vague'

  const handleChange = (t: string, b: string) => {
    setTitle(t)
    setBody(b)
    onChange(id, t, b)
  }

  return (
    <div className="chat-card draft-chat-card">
      <div className="card-header">
        <span className="card-ai-tag">AI</span>
        <span className="card-title">预览要发送的内容</span>
        <CopyButton text={`${title}\n\n${body}`} />
      </div>

      <div className="privacy-warn-box">
        <strong>下面这段会被家长看到。</strong>
        请确认没有你暂时不想分享的细节。默认内容是降敏摘要，你可以手动加入想说的具体内容。
      </div>

      {scope === 'vague' && (
        <div className="vague-note">
          模糊提醒模式：家长只会看到"孩子想跟你聊聊"，看不到你具体说了什么。
        </div>
      )}

      <div className="draft-block">
        <label className="block-label">标题</label>
        <input
          className="card-input"
          value={title}
          onChange={(e) => handleChange(e.target.value, body)}
          disabled={sent}
        />
      </div>

      <div className="draft-block">
        <label className="block-label">内容</label>
        <textarea
          className="card-input"
          value={body}
          onChange={(e) => handleChange(title, e.target.value)}
          rows={6}
          disabled={sent}
        />
      </div>

      {!sent && (
        <button
          type="button"
          className="card-primary-btn"
          onClick={() => onSend(id, title, body, draft.isVague)}
        >
          {willSend ? '确认发送到家长端' : '确认保存草稿'}
        </button>
      )}
      {sent && (
        <div className="card-done-tag">
          {willSend ? '已发送到家长端' : '草稿已保存'}
        </div>
      )}
    </div>
  )
}
