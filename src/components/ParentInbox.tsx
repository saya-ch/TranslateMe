import { useEffect, useState } from 'react'
import { getParentInbox, subscribe, markRead, loadDemoMessages } from '../lib/messageStore'
import type { InboxMessage } from '../types'

interface ParentInboxProps {
  onOpenMessage: (msg: InboxMessage) => void
  onAskAI: () => void
  onReset: () => void
}

function formatTime(ts: number): string {
  const diff = Date.now() - ts
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hr = Math.floor(min / 60)
  return `${hr} 小时前`
}

export function ParentInbox({ onOpenMessage, onAskAI, onReset }: ParentInboxProps) {
  const [messages, setMessages] = useState<InboxMessage[]>(getParentInbox())

  useEffect(() => {
    return subscribe(() => setMessages(getParentInbox()))
  }, [])

  const handleOpen = (m: InboxMessage) => {
    markRead(m.id)
    onOpenMessage(m)
  }

  return (
    <div className="inbox-panel">
      <p className="panel-hint">
        这里是孩子通过帮我说出口发来的沟通请求。你看到的是温和摘要，不是孩子原话。
      </p>

      <button
        type="button"
        className="demo-btn"
        onClick={() => loadDemoMessages()}
      >
        加载演示案例（方便评委快速查看效果）
      </button>

      {messages.length === 0 && (
        <div className="empty-state">暂无沟通请求</div>
      )}

      <div className="message-list">
        {messages.map((m) => (
          <button
            key={m.id}
            type="button"
            className={`message-item ${m.read ? '' : 'unread'}`}
            onClick={() => handleOpen(m)}
          >
            <div className="message-icon">💬</div>
            <div className="message-content">
              <div className="message-title">{m.title}</div>
              <div className="message-time">{formatTime(m.createdAt)}</div>
            </div>
            {!m.read && <span className="unread-dot" />}
          </button>
        ))}
      </div>

      <button type="button" className="ghost-btn" onClick={onAskAI}>
        我不知道怎么回应，问问 AI
      </button>
      <button type="button" className="ghost-btn" onClick={onReset}>
        返回首页
      </button>
    </div>
  )
}
