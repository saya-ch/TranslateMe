import { useEffect, useState } from 'react'
import { getChildInbox, subscribe } from '../lib/messageStore'
import type { InboxMessage } from '../types'

interface ChildInboxProps {
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

export function ChildInbox({ onReset }: ChildInboxProps) {
  const [messages, setMessages] = useState<InboxMessage[]>(getChildInbox())
  const [opened, setOpened] = useState<InboxMessage | null>(null)

  useEffect(() => {
    return subscribe(() => setMessages(getChildInbox()))
  }, [])

  return (
    <div className="inbox-panel">
      <p className="panel-hint">这里是你收到的家长回应。</p>

      {messages.length === 0 && (
        <div className="empty-state">暂无消息</div>
      )}

      <div className="message-list">
        {messages.map((m) => (
          <button
            key={m.id}
            type="button"
            className={`message-item ${m.read ? '' : 'unread'}`}
            onClick={() => setOpened(m)}
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

      {opened && (
        <div className="message-detail">
          <div className="message-detail-title">{opened.title}</div>
          <p className="message-detail-body">{opened.body}</p>
          <button
            type="button"
            className="ghost-btn"
            onClick={() => setOpened(null)}
          >
            关闭
          </button>
        </div>
      )}

      <button type="button" className="ghost-btn" onClick={onReset}>
        返回首页
      </button>
    </div>
  )
}
