import type { TeacherGuide } from '../../../types'
import { CopyButton } from '../../CopyButton'

interface TeacherGuideChatCardProps {
  guide: TeacherGuide
}

export function TeacherGuideChatCard({ guide }: TeacherGuideChatCardProps) {
  const fullText = `【情况摘要】\n${guide.summary}\n\n【隐私提醒】\n${guide.privacyNote}\n\n【谈话建议】\n${guide.talkAdvice.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n【观察点】\n${guide.observePoints.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n【转介建议】\n${guide.referAdvice}`

  return (
    <div className="chat-card guide-chat-card teacher-guide-card">
      <div className="card-header">
        <span className="card-ai-tag">AI</span>
        <span className="card-title">老师端建议</span>
        <CopyButton text={fullText} />
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">情况摘要</div>
        <p className="guide-text">{guide.summary}</p>
      </div>

      <div className="guide-section privacy-section">
        <div className="guide-subtitle">隐私提醒</div>
        <p className="guide-text">{guide.privacyNote}</p>
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">谈话建议</div>
        <ol className="guide-list">
          {guide.talkAdvice.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </div>

      <div className="guide-section">
        <div className="guide-subtitle">观察点</div>
        <ul className="guide-list">
          {guide.observePoints.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </div>

      <div className="guide-section refer-section">
        <div className="guide-subtitle">转介建议</div>
        <p className="guide-text">{guide.referAdvice}</p>
      </div>

      <p className="card-hint">
        你可以选择只记录暂不行动，或之后走学校心理老师/家校沟通流程。本工具不会自动告知家长。
      </p>
    </div>
  )
}
