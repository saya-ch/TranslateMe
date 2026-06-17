import { useState } from 'react'
import type { ParentGuide } from '../types'
import { CopyButton } from './CopyButton'

interface ParentGuidePanelProps {
  guide: ParentGuide
  onConfirmReply: (replyBody: string) => void
  onBack: () => void
}

export function ParentGuidePanel({ guide, onConfirmReply, onBack }: ParentGuidePanelProps) {
  const [reply, setReply] = useState(guide.replyDraft)

  return (
    <div className="guide-panel">
      <div className="firewall-note">
        <strong>信息防火墙：</strong>
        {guide.firewallNote}
      </div>

      <section className="guide-card">
        <h3 className="guide-title">破冰建议</h3>
        <p className="guide-text">{guide.iceBreaker}</p>
      </section>

      <section className="guide-card">
        <h3 className="guide-title">可以说的三句话</h3>
        <ol className="guide-list">
          {guide.sayThree.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </section>

      <section className="guide-card">
        <h3 className="guide-title">暂时不要说的三句话</h3>
        <ol className="guide-list not-list">
          {guide.notSayThree.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </section>

      <section className="guide-card">
        <h3 className="guide-title">下一步建议</h3>
        <p className="guide-text">{guide.nextStep}</p>
      </section>

      <section className="guide-card reply-card">
        <div className="guide-head-row">
          <h3 className="guide-title">给孩子的回应草稿</h3>
          <CopyButton text={reply} />
        </div>
        <p className="panel-hint">这是 AI 帮你写的草稿，你可以随便改。确认后会发到孩子端。</p>
        <textarea
          className="input-box"
          value={reply}
          onChange={(e) => setReply(e.target.value)}
          rows={5}
        />
      </section>

      <div className="btn-row">
        <button type="button" className="ghost-btn" onClick={onBack}>
          返回
        </button>
        <button
          type="button"
          className="primary-btn"
          onClick={() => onConfirmReply(reply)}
        >
          确认发送给孩子
        </button>
      </div>
    </div>
  )
}
