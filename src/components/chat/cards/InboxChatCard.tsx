import type { InboxMessage } from '../../../types'

interface InboxChatCardProps {
  message: InboxMessage
  onOpen: () => void
}

function formatTime(ts: number): string {
  const diff = Date.now() - ts
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hr = Math.floor(min / 60)
  return `${hr} 小时前`
}

export function InboxChatCard({ message, onOpen }: InboxChatCardProps) {
  return (
    <div className="chat-card inbox-chat-card">
      <div className="card-header">
        <span className="card-ai-tag">AI</span>
        <span className="card-title">收到一条消息</span>
      </div>

      <button type="button" className="inbox-msg-btn" onClick={onOpen}>
        <div className="inbox-msg-icon">💬</div>
        <div className="inbox-msg-content">
          <div className="inbox-msg-title">{message.title}</div>
          <div className="inbox-msg-time">{formatTime(message.createdAt)}</div>
        </div>
        {!message.read && <span className="unread-dot" />}
      </button>

      <p className="card-hint">
        {message.from === 'child'
          ? '这是孩子确认后的提醒，不是原话。孩子选择把这段发给你看。'
          : '这是家长发来的回应。'}
      </p>
    </div>
  )
}
