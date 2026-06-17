import { useState } from 'react'
import type { ParentGuide } from '../../../types'
import { CopyButton } from '../../CopyButton'

interface GuideChatCardProps {
  id: string
  guide: ParentGuide
  isFirewall?: boolean
  replySent?: boolean
  onReplySend: (id: string, replyBody: string) => void
}

export function GuideChatCard({
  id,
  guide,
  isFirewall,
  replySent,
  onReplySend,
}: GuideChatCardProps) {
  const [reply, setReply] = useState(guide.replyDraft)

  return (
    <div className={`chat-card guide-chat-card ${isFirewall ? 'firewall-card' : ''}`}>
      <div className="card-header">
        <span className={`card-ai-tag ${isFirewall ? 'safety-tag' : ''}`}>AI</span>
        <span className="card-title">
          {isFirewall ? '信息防火墙提醒' : 'AI 给你的建议'}
        </span>
      </div>

      <div className={`firewall-note ${isFirewall ? 'firewall-strong' : ''}`}>
        {guide.firewallNote}
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">破冰建议</div>
        <p className="guide-text">{guide.iceBreaker}</p>
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">可以说的三句话</div>
        <ol className="guide-list">
          {guide.sayThree.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">暂时不要说的三句话</div>
        <ol className="guide-list not-list">
          {guide.notSayThree.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">下一步建议</div>
        <p className="guide-text">{guide.nextStep}</p>
      </div>

      <div className="guide-section reply-section">
        <div className="guide-head-row">
          <div className="guide-subtitle">给孩子的回应草稿</div>
          <CopyButton text={reply} />
        </div>
        <p className="card-hint">这是 AI 帮你写的草稿，你可以随便改。确认后会发到孩子端。</p>
        <textarea
          className="card-input"
          value={reply}
          onChange={(e) => setReply(e.target.value)}
          rows={5}
          disabled={replySent}
        />
        {!replySent && (
          <button
            type="button"
            className="card-primary-btn"
            onClick={() => onReplySend(id, reply)}
          >
            确认发送给孩子
          </button>
        )}
        {replySent && <div className="card-done-tag">回应已发送给孩子</div>}
      </div>
    </div>
  )
}
