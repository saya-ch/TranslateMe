import type { InboxMessage } from '../types'

interface ParentMessageViewProps {
  message: InboxMessage
  onAskAI: () => void
  onBack: () => void
}

export function ParentMessageView({ message, onAskAI, onBack }: ParentMessageViewProps) {
  return (
    <div className="message-view-panel">
      <p className="panel-hint">
        这是孩子发来的沟通请求。你看到的是温和摘要，不是孩子原话。
      </p>

      {message.isVague && (
        <div className="vague-note">
          孩子选择了"模糊提醒"模式，所以你看不到具体内容，只知道 ta 想跟你聊聊。
        </div>
      )}

      <div className="message-detail-card">
        <div className="message-detail-title">{message.title}</div>
        <p className="message-detail-body">{message.body}</p>
      </div>

      <button type="button" className="primary-btn" onClick={onAskAI}>
        我不知道怎么回应，问问 AI
      </button>
      <button type="button" className="ghost-btn" onClick={onBack}>
        返回收件箱
      </button>
    </div>
  )
}
