// 家长端对话控制器
// 默认走后端 API，失败时回退到本地模拟

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ChatMessage, InboxMessage, ParentStage } from '../types'
import { buildParentGuide } from '../lib/parentBuilder'
import {
  getParentInbox,
  loadDemoMessages,
  markRead,
  parentSendReplyToChild,
  subscribe,
} from '../lib/messageStore'
import { nextId } from '../components/chat/ChatMessageList'
import {
  ApiError,
  fetchInbox,
  listAccessibleChildren,
  parentAsk,
  replyToChild,
  type AuthUser,
  type InboxItemDTO,
} from '../lib/apiClient'

const AI_GREETING =
  '你好。如果孩子通过帮我说出口发来沟通请求，会出现在这里。你也可以直接问我怎么跟孩子沟通。'

interface ControllerProps {
  authUser: AuthUser | null
  useLocalMode: boolean
}

// 将后端 InboxItemDTO 转换为前端 InboxMessage
function dtoToInboxMessage(dto: InboxItemDTO): InboxMessage {
  return {
    id: dto.id,
    from: (dto.from_role === 'child' ? 'child' : 'parent') as 'child' | 'parent',
    title: dto.title,
    body: dto.body,
    isVague: dto.level <= 1,
    createdAt: new Date(dto.delivered_at).getTime(),
    read: dto.read,
  }
}

export function useParentController({ authUser, useLocalMode }: ControllerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<ParentStage>('initial')

  // 当前选中的 child_id（家长可访问的孩子）
  const childIdRef = useRef<string | null>(null)

  // 订阅收件箱变化
  const [, forceUpdate] = useState(0)
  useEffect(() => {
    const unsubscribe = subscribe(() => forceUpdate((n) => n + 1))
    return unsubscribe
  }, [])

  const updateMessage = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? ({ ...m, ...patch } as ChatMessage) : m)),
    )
  }, [])

  const canUseBackend = !!authUser && !useLocalMode

  // 挂载时拉取可访问的孩子列表，自动选中第一个
  useEffect(() => {
    if (!canUseBackend) return
    let cancelled = false
    ;(async () => {
      try {
        const children = await listAccessibleChildren()
        if (cancelled) return
        if (children.length > 0) {
          childIdRef.current = children[0].child_id
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'text',
              text: `已连接后端，当前关注孩子：${children[0].display_name}。你可以查看收件箱或直接提问。`,
            },
          ])
        } else {
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'text',
              text: '已连接后端，但你的账号还未加入任何家庭组。请联系管理员将你加入孩子的家庭组。',
            },
          ])
        }
      } catch (e) {
        const err = e as ApiError
        console.warn('[parent] 拉取可访问孩子列表失败:', err.detail)
      }
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canUseBackend])

  // 用户发送文本（家长提问）
  const handleUserText = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return

      setMessages((prev) => [
        ...prev,
        { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
      ])

      // 后端模式：调用 /llm/parent-ask
      if (canUseBackend && childIdRef.current) {
        try {
          const result = await parentAsk({
            child_id: childIdRef.current,
            question: trimmed,
          })

          const content = result.content
          const guide = {
            firewallNote:
              content._note || content.firewall_note || '通用沟通建议。',
            iceBreaker: content.icebreaker || '',
            sayThree: content.say_three || [],
            notSayThree: content.not_say_three || [],
            nextStep: content.next_step || '',
            replyDraft: content.reply_draft || '',
          }
          const isFirewall = result.is_probing

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
          return
        } catch (e) {
          const err = e as ApiError
          console.warn('[parent] 后端 parent-ask 失败，回退本地:', err.detail)
          // 继续走本地流程
        }
      }

      // 本地模式
      const guide = buildParentGuide(trimmed)
      const isFirewall =
        guide.firewallNote.includes('我不能透露') &&
        guide.firewallNote.includes('具体')
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
    },
    [canUseBackend],
  )

  // 家长回应发送
  const handleReplySend = useCallback(
    async (id: string, replyBody: string) => {
      // 后端模式：调用 /conversations/reply
      if (canUseBackend && childIdRef.current) {
        try {
          await replyToChild({
            child_id: childIdRef.current,
            to_role: 'child',
            body: replyBody,
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
          return
        } catch (e) {
          const err = e as ApiError
          console.warn('[parent] 后端回复失败，回退本地:', err.detail)
          // 继续走本地流程
        }
      }

      // 本地模式
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
    [canUseBackend, updateMessage],
  )

  // 查看收件箱
  const triggerInbox = useCallback(async () => {
    // 后端模式：调用 /conversations/inbox
    if (canUseBackend) {
      try {
        const items = await fetchInbox(childIdRef.current || undefined)
        if (items.length === 0) {
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
        items.forEach((dto) => {
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'inbox-card',
              message: dtoToInboxMessage(dto),
            },
          ])
        })
        return
      } catch (e) {
        const err = e as ApiError
        console.warn('[parent] 后端收件箱拉取失败，回退本地:', err.detail)
        // 继续走本地流程
      }
    }

    // 本地模式
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
  }, [canUseBackend])

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
