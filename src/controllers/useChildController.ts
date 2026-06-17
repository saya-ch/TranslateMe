// 孩子端对话控制器
// 默认走后端 API，失败时回退到本地模拟

import { useCallback, useMemo, useRef, useState } from 'react'
import type {
  ChatMessage,
  ChildClarify,
  ChildStage,
  ShareScope,
} from '../types'
import { needsSafetyCheck } from '../lib/safety'
import {
  buildClarifyDraft,
  buildParentMessageDraft,
  isActuallySent,
} from '../lib/childBuilder'
import {
  childSendMessageToParent,
  getChildInbox,
  markRead,
  subscribe,
} from '../lib/messageStore'
import { nextId } from '../components/chat/ChatMessageList'
import {
  ApiError,
  confirmDraft,
  sendChildMessage,
  type AuthUser,
} from '../lib/apiClient'

const AI_GREETING =
  '你可以先随便说一句，不用说完整。这里默认只有你自己能看到。'

interface ControllerProps {
  authUser: AuthUser | null
  useLocalMode: boolean
}

export function useChildController({ authUser, useLocalMode }: ControllerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<ChildStage>('initial')
  const [rawInput, setRawInput] = useState('')
  const [clarify, setClarify] = useState<ChildClarify | null>(null)
  const [scope, setScope] = useState<ShareScope | null>(null)

  // 后端会话 id（首次发送后保存）
  const conversationIdRef = useRef<string | null>(null)
  // 后端草稿 id（用于确认分享）
  const draftIdRef = useRef<string | null>(null)

  // 订阅收件箱变化（用于家长回应到达时刷新）
  const [, forceUpdate] = useState(0)
  useMemo(() => subscribe(() => forceUpdate((n) => n + 1)), [])

  const updateMessage = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? ({ ...m, ...patch } as ChatMessage) : m)),
    )
  }, [])

  const canUseBackend = !!authUser && !useLocalMode && !!authUser.child_profile_id

  // 用户发送文本
  const handleUserText = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return

      setMessages((prev) => [
        ...prev,
        { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
      ])

      // 安全确认检测（前端先做一次，后端也会做）
      if (needsSafetyCheck(trimmed)) {
        setRawInput(trimmed)
        setStage('safety')
        setMessages((prev) => [
          ...prev,
          {
            id: nextId('ai'),
            role: 'ai',
            type: 'safety-card',
            choice: null,
          },
        ])
        return
      }

      // 后端模式：调用 /conversations/chat
      if (canUseBackend) {
        try {
          const result = await sendChildMessage({
            conversation_id: conversationIdRef.current,
            child_id: authUser.child_profile_id!,
            text: trimmed,
          })
          conversationIdRef.current = result.conversation_id

          // 后端返回安全检测命中
          if (result.needs_safety_check) {
            setRawInput(trimmed)
            setStage('safety')
            setMessages((prev) => [
              ...prev,
              {
                id: nextId('ai'),
                role: 'ai',
                type: 'safety-card',
                choice: null,
              },
            ])
            return
          }

          // 后端返回草稿
          if (result.draft) {
            draftIdRef.current = result.draft.draft_id
            setRawInput(trimmed)
            setStage('input-done')
            const draftClarify = buildClarifyDraft(trimmed)
            setClarify(draftClarify)
            setMessages((prev) => [
              ...prev,
              {
                id: nextId('ai'),
                role: 'ai',
                type: 'text',
                text: '收到了。后端已生成草稿，你可以点下方的"整理我想说的"查看。',
              },
              {
                id: nextId('ai'),
                role: 'ai',
                type: 'clarify-card',
                clarify: draftClarify,
                confirmed: false,
              },
            ])
            return
          }

          // 无草稿（可能因安全风险被跳过）
          setRawInput(trimmed)
          setStage('input-done')
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'text',
              text: '收到了。你可以点下方的"整理我想说的"，我帮你把这句话整理成几个问题。',
            },
          ])
          return
        } catch (e) {
          const err = e as ApiError
          console.warn('[child] 后端调用失败，回退本地模式:', err.detail)
          // 继续走本地流程
        }
      }

      // 本地流程：记录输入，等待用户点"整理我想说的"
      setRawInput(trimmed)
      setStage('input-done')
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '收到了。你可以点下方的"整理我想说的"，我帮你把这句话整理成几个问题。',
        },
      ])
    },
    [canUseBackend, authUser],
  )

  // 触发整理卡
  const triggerClarify = useCallback(() => {
    if (stage !== 'input-done' || !rawInput) return
    const draft = buildClarifyDraft(rawInput)
    setClarify(draft)
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'clarify-card',
        clarify: draft,
        confirmed: false,
      },
    ])
  }, [stage, rawInput])

  // 整理卡确认
  const handleClarifyConfirm = useCallback(
    (id: string, c: ChildClarify) => {
      setClarify(c)
      setStage('clarify-done')
      updateMessage(id, { clarify: c, confirmed: true } as Partial<ChatMessage>)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '整理好了。接下来你想怎么处理这段话？可以点下方的"选择分享范围"。',
        },
      ])
    },
    [updateMessage],
  )

  // 整理卡返回
  const handleClarifyBack = useCallback(
    (id: string) => {
      setMessages((prev) => prev.filter((m) => m.id !== id))
      setStage('input-done')
    },
    [],
  )

  // 触发分享范围卡
  const triggerScope = useCallback(() => {
    if (stage !== 'clarify-done') return
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'scope-card',
        selected: null,
      },
    ])
  }, [stage])

  // 分享范围选择
  const handleScopeSelect = useCallback(
    (id: string, s: ShareScope) => {
      setScope(s)
      setStage('scope-done')
      updateMessage(id, { selected: s } as Partial<ChatMessage>)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '好的。你可以点下方的"预览要发送的内容"看看会发给家长什么。',
        },
      ])
    },
    [updateMessage],
  )

  // 触发预览卡
  const triggerDraft = useCallback(() => {
    if (stage !== 'scope-done' || !clarify || !scope) return
    const draft = buildParentMessageDraft(clarify, scope)
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'draft-card',
        draft,
        scope,
        sent: false,
      },
    ])
  }, [stage, clarify, scope])

  // 预览卡内容变化
  const handleDraftChange = useCallback(
    (id: string, title: string, body: string) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === id && m.type === 'draft-card'
            ? { ...m, draft: { ...m.draft, title, body } }
            : m,
        ),
      )
    },
    [],
  )

  // 预览卡发送
  const handleDraftSend = useCallback(
    async (id: string, title: string, body: string, isVague: boolean) => {
      const shouldSend = scope ? isActuallySent(scope) : false

      // 后端模式：调用 /drafts/{id}/confirm
      if (canUseBackend && draftIdRef.current && shouldSend) {
        try {
          await confirmDraft({
            draft_id: draftIdRef.current,
            to_role: 'parent',
            level: isVague ? 1 : 3,
          })
          updateMessage(id, {
            draft: { title, body, isVague },
            sent: true,
          } as Partial<ChatMessage>)
          setStage('sent')
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'text',
              text: '已发送到家长端。家长会看到你确认后的内容，看不到你的原始输入和未分享的部分。',
            },
          ])
          return
        } catch (e) {
          const err = e as ApiError
          console.warn('[child] 后端确认草稿失败，回退本地:', err.detail)
          // 继续走本地流程
        }
      }

      // 本地模式
      if (shouldSend) {
        childSendMessageToParent({ title, body, isVague })
      }
      updateMessage(id, {
        draft: { title, body, isVague },
        sent: true,
      } as Partial<ChatMessage>)
      setStage('sent')
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: shouldSend
            ? '已发送到家长端。家长会看到你确认后的内容，看不到你的原始输入和未分享的部分。'
            : '草稿已保存。这份草稿只有你自己能看到，你可以稍后自己决定怎么发。',
        },
      ])
    },
    [scope, canUseBackend, updateMessage],
  )

  // 安全确认选择
  const handleSafetyChoice = useCallback(
    (id: string, choice: 'safe' | 'unsafe') => {
      updateMessage(id, { choice } as Partial<ChatMessage>)
      if (choice === 'safe') {
        // 继续整理流程
        const draft = buildClarifyDraft(rawInput)
        setClarify(draft)
        setStage('input-done')
        setMessages((prev) => [
          ...prev,
          {
            id: nextId('ai'),
            role: 'ai',
            type: 'text',
            text: '好的，我们继续。你可以点下方的"整理我想说的"。',
          },
        ])
      } else {
        // 不安全分支：只显示支持资源
        setStage('safety')
        setMessages((prev) => [
          ...prev,
          {
            id: nextId('ai'),
            role: 'ai',
            type: 'text',
            text: '谢谢你愿意告诉我们。你现在不需要继续整理表达，请先联系：12355 青少年服务热线 / 12356 心理援助热线 / 身边可信成年人 / 学校心理老师。如存在立即人身危险，请拨打 110 / 120。',
          },
        ])
      }
    },
    [rawInput, updateMessage],
  )

  // 查看收件箱
  const triggerInbox = useCallback(() => {
    const inbox = getChildInbox()
    if (inbox.length === 0) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '暂无消息。如果家长通过帮我说出口回应了你，会出现在这里。',
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

  // 上下文感知的快捷操作
  const quickActions = useMemo(() => {
    const actions: { key: string; label: string; onClick: () => void }[] = []
    if (stage === 'input-done') {
      actions.push({ key: 'clarify', label: '整理我想说的', onClick: triggerClarify })
    }
    if (stage === 'clarify-done') {
      actions.push({ key: 'scope', label: '选择分享范围', onClick: triggerScope })
    }
    if (stage === 'scope-done') {
      actions.push({ key: 'draft', label: '预览要发送的内容', onClick: triggerDraft })
    }
    actions.push({ key: 'inbox', label: '查看收件箱', onClick: triggerInbox })
    return actions
  }, [stage, triggerClarify, triggerScope, triggerDraft, triggerInbox])

  return {
    messages,
    stage,
    quickActions,
    handleUserText,
    handleClarifyConfirm,
    handleClarifyBack,
    handleScopeSelect,
    handleDraftChange,
    handleDraftSend,
    handleSafetyChoice,
  }
}
