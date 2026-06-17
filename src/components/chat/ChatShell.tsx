import { useEffect, useRef, type ReactNode } from 'react'
import type { Identity, ChatMessage, ChildClarify, ShareScope } from '../../types'
import { ChatMessageList } from './ChatMessageList'
import { QuickActions } from './QuickActions'
import { ChatInput } from './ChatInput'

interface ChatShellProps {
  identity: Identity
  messages: ChatMessage[]
  quickActions: { key: string; label: string; onClick: () => void }[]
  inputPlaceholder?: string
  onSendText: (text: string) => void
  onSwitchIdentity: () => void
  // 孩子端回调
  onClarifyConfirm?: (id: string, clarify: ChildClarify) => void
  onClarifyBack?: (id: string) => void
  onScopeSelect?: (id: string, scope: ShareScope) => void
  onDraftChange?: (id: string, title: string, body: string) => void
  onDraftSend?: (id: string, title: string, body: string, isVague: boolean) => void
  onSafetyChoice?: (id: string, choice: 'safe' | 'unsafe') => void
  // 家长端回调
  onParentReplySend?: (id: string, replyBody: string) => void
  onOpenInboxMessage?: (messageId: string) => void
  children?: ReactNode
}

const IDENTITY_LABEL: Record<Identity, string> = {
  student: '我是学生',
  parent: '我是家长',
  teacher: '我是老师',
}

export function ChatShell(props: ChatShellProps) {
  const {
    identity,
    messages,
    quickActions,
    inputPlaceholder,
    onSendText,
    onSwitchIdentity,
  } = props

  const scrollRef = useRef<HTMLDivElement>(null)

  // 新消息时自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="chat-shell">
      <header className="chat-header">
        <div className="chat-header-left">
          <h1 className="chat-title">帮我说出口</h1>
          <span className="chat-identity-tag">{IDENTITY_LABEL[identity]}</span>
        </div>
        <button
          type="button"
          className="chat-switch-btn"
          onClick={onSwitchIdentity}
        >
          切换身份
        </button>
      </header>

      <div className="chat-scroll" ref={scrollRef}>
        <ChatMessageList
          messages={messages}
          onClarifyConfirm={props.onClarifyConfirm || (() => {})}
          onClarifyBack={props.onClarifyBack || (() => {})}
          onScopeSelect={props.onScopeSelect || (() => {})}
          onDraftChange={props.onDraftChange || (() => {})}
          onDraftSend={props.onDraftSend || (() => {})}
          onSafetyChoice={props.onSafetyChoice || (() => {})}
          onParentReplySend={props.onParentReplySend || (() => {})}
          onOpenInboxMessage={props.onOpenInboxMessage || (() => {})}
        />
      </div>

      <div className="chat-bottom">
        <QuickActions actions={quickActions} onSwitchIdentity={onSwitchIdentity} />
        <ChatInput onSend={onSendText} placeholder={inputPlaceholder} />
      </div>
    </div>
  )
}
