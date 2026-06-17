import { useState } from 'react'
import type { ChatMessage, ChildClarify, ShareScope } from '../../types'
import { ChatBubble } from './ChatBubble'
import { ClarifyChatCard } from './cards/ClarifyChatCard'
import { ScopeChatCard } from './cards/ScopeChatCard'
import { DraftChatCard } from './cards/DraftChatCard'
import { SafetyChatCard } from './cards/SafetyChatCard'
import { InboxChatCard } from './cards/InboxChatCard'
import { GuideChatCard } from './cards/GuideChatCard'
import { TeacherGuideChatCard } from './cards/TeacherGuideChatCard'

interface ChatMessageListProps {
  messages: ChatMessage[]
  // 孩子端回调
  onClarifyConfirm: (id: string, clarify: ChildClarify) => void
  onClarifyBack: (id: string) => void
  onScopeSelect: (id: string, scope: ShareScope) => void
  onDraftChange: (id: string, title: string, body: string) => void
  onDraftSend: (id: string, title: string, body: string, isVague: boolean) => void
  onSafetyChoice: (id: string, choice: 'safe' | 'unsafe') => void
  // 家长端回调
  onParentReplySend: (id: string, replyBody: string) => void
  onOpenInboxMessage: (messageId: string) => void
}

export function ChatMessageList(props: ChatMessageListProps) {
  const { messages } = props

  return (
    <div className="chat-message-list">
      {messages.map((msg) => {
        if (msg.role === 'user') {
          return (
            <ChatBubble key={msg.id} role="user">
              {msg.text}
            </ChatBubble>
          )
        }

        // AI 消息
        switch (msg.type) {
          case 'text':
            return (
              <ChatBubble key={msg.id} role="ai">
                {msg.text}
              </ChatBubble>
            )
          case 'clarify-card':
            return (
              <ClarifyChatCard
                key={msg.id}
                id={msg.id}
                clarify={msg.clarify}
                confirmed={msg.confirmed}
                onConfirm={props.onClarifyConfirm}
                onBack={props.onClarifyBack}
              />
            )
          case 'scope-card':
            return (
              <ScopeChatCard
                key={msg.id}
                id={msg.id}
                selected={msg.selected}
                onSelect={props.onScopeSelect}
              />
            )
          case 'draft-card':
            return (
              <DraftChatCard
                key={msg.id}
                id={msg.id}
                draft={msg.draft}
                scope={msg.scope}
                sent={msg.sent}
                onChange={props.onDraftChange}
                onSend={props.onDraftSend}
              />
            )
          case 'safety-card':
            return (
              <SafetyChatCard
                key={msg.id}
                id={msg.id}
                choice={msg.choice}
                onChoose={props.onSafetyChoice}
              />
            )
          case 'inbox-card':
            return (
              <InboxChatCard
                key={msg.id}
                message={msg.message}
                onOpen={() => props.onOpenInboxMessage(msg.message.id)}
              />
            )
          case 'guide-card':
            return (
              <GuideChatCard
                key={msg.id}
                id={msg.id}
                guide={msg.guide}
                isFirewall={msg.isFirewall}
                replySent={msg.replySent}
                onReplySend={props.onParentReplySend}
              />
            )
          case 'teacher-guide-card':
            return <TeacherGuideChatCard key={msg.id} guide={msg.guide} />
          default:
            return null
        }
      })}
    </div>
  )
}

// 用于在组件外生成稳定 id 的工具
let _seq = 0
export function nextId(prefix: string): string {
  _seq += 1
  return `${prefix}-${Date.now()}-${_seq}`
}

// 供输入框使用的受控状态 hook 占位（避免未使用警告）
export function useDraftBody(initial: string) {
  return useState(initial)
}
