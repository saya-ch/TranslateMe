// 家长端对话控制器

import { useCallback, useMemo, useState } from 'react'
import type { ChatMessage, ParentStage } from '../types'
import { buildParentGuide } from '../lib/parentBuilder'
import {
  getParentInbox,
  loadDemoMessages,
  markRead,
  parentSendReplyToChild,
  subscribe,
} from '../lib/messageStore'
import { nextId } from '../components/chat/ChatMessageList'

const AI_GREETING =
  '你好。如果孩子通过帮我说出口发来沟通请求，会出现在这里。你也可以直接问我怎么跟孩子沟通。'

export function useParentController() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<ParentStage>('initial')

  // 订阅收件箱变化
  const [, forceUpdate] = useState(0)
  useMemo(() => subscribe(() => forceUpdate((n) => n + 1)), [])

  const updateMessage = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? ({ ...m, ...patch } as ChatMessage) : m)),
    )
  }, [])

  // 用户发送文本（家长提问）
  const handleUserText = useCallback((text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return

    setMessages((prev) => [
      ...prev,
      { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
    ])

    const guide = buildParentGuide(trimmed)
    const isFirewall = guide.firewallNote.includes('我不能透露') && guide.firewallNote.includes('具体')
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'guide-card',
        guide,
        isFirewall,
        replySent: false,
      },
    ])
    setStage('guide-shown')
  }, [])

  // 家长回应发送
  const handleReplySend = useCallback(
    (id: string, replyBody: string) => {
      parentSendReplyToChild({
        title: '家长通过帮我说出口发来一条回应',
        body: replyBody,
        isVague: false,
      })
      updateMessage(id, { replySent: true } as Partial<ChatMessage>)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '回应已发送给孩子。孩子会在 ta 的收件箱看到你的回应。记住，先听不评价，比说什么都重要。',
        },
      ])
    },
    [updateMessage],
  )

  // 查看收件箱
  const triggerInbox = useCallback(() => {
    const inbox = getParentInbox()
    if (inbox.length === 0) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '暂无沟通请求。如果孩子通过帮我说出口发来沟通请求，会出现在这里。',
        },
      ])
      return
    }
    inbox.forEach((m) => {
      markRead(m.id)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'inbox-card',
          message: m,
        },
      ])
    })
  }, [])

  // 加载演示案例
  const triggerDemo = useCallback(() => {
    loadDemoMessages()
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'text',
        text: '已加载演示案例。你可以点"查看收件箱"看到孩子发来的沟通请求。',
      },
    ])
  }, [])

  const quickActions = useMemo(() => {
    return [
      { key: 'inbox', label: '查看收件箱', onClick: triggerInbox },
      { key: 'demo', label: '加载演示案例', onClick: triggerDemo },
    ]
  }, [triggerInbox, triggerDemo])

  return {
    messages,
    stage,
    quickActions,
    handleUserText,
    handleReplySend,
  }
}
