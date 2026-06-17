import type { TeacherGuide } from '../types'
import { CopyButton } from './CopyButton'

interface TeacherGuidePanelProps {
  guide: TeacherGuide
  onReset: () => void
}

export function TeacherGuidePanel({ guide, onReset }: TeacherGuidePanelProps) {
  const fullText = `【情况摘要】\n${guide.summary}\n\n【隐私提醒】\n${guide.privacyNote}\n\n【谈话建议】\n${guide.talkAdvice.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n【观察点】\n${guide.observePoints.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n【转介建议】\n${guide.referAdvice}`

  return (
    <div className="guide-panel">
      <div className="guide-head-row">
        <h3 className="guide-title">老师端建议</h3>
        <CopyButton text={fullText} />
      </div>

      <section className="guide-card">
        <h4 className="guide-subtitle">情况摘要</h4>
        <p className="guide-text">{guide.summary}</p>
      </section>

      <section className="guide-card privacy-card">
        <h4 className="guide-subtitle">隐私提醒</h4>
        <p className="guide-text">{guide.privacyNote}</p>
      </section>

      <section className="guide-card">
        <h4 className="guide-subtitle">谈话建议</h4>
        <ol className="guide-list">
          {guide.talkAdvice.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </section>

      <section className="guide-card">
        <h4 className="guide-subtitle">观察点</h4>
        <ul className="guide-list">
          {guide.observePoints.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </section>

      <section className="guide-card refer-card">
        <h4 className="guide-subtitle">转介建议</h4>
        <p className="guide-text">{guide.referAdvice}</p>
      </section>

      <div className="action-row">
        <p className="panel-hint">
          你可以选择只记录暂不行动，或之后走学校心理老师/家校沟通流程。本工具不会自动告知家长。
        </p>
      </div>

      <button type="button" className="ghost-btn" onClick={onReset}>
        返回首页
      </button>
    </div>
  )
}
