import type { ReactNode } from 'react'

interface ChatBubbleProps {
  role: 'ai' | 'user'
  children: ReactNode
}

export function ChatBubble({ role, children }: ChatBubbleProps) {
  return (
    <div className={`chat-bubble ${role === 'ai' ? 'ai-bubble' : 'user-bubble'}`}>
      {role === 'ai' && <div className="ai-avatar">AI</div>}
      <div className="bubble-content">{children}</div>
    </div>
  )
}
