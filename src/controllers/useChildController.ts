// 孩子端对话控制器
// 负责孩子端的消息流转、阶段管理、快捷操作上下文

import { useCallback, useMemo, useState } from 'react'
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

const AI_GREETING =
  '你可以先随便说一句，不用说完整。这里默认只有你自己能看到。'

export function useChildController() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<ChildStage>('initial')
  const [rawInput, setRawInput] = useState('')
  const [clarify, setClarify] = useState<ChildClarify | null>(null)
  const [scope, setScope] = useState<ShareScope | null>(null)

  // 订阅收件箱变化（用于家长回应到达时刷新）
  const [, forceUpdate] = useState(0)
  useMemo(() => subscribe(() => forceUpdate((n) => n + 1)), [])

  const updateMessage = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? ({ ...m, ...patch } as ChatMessage) : m)),
    )
  }, [])

  // 用户发送文本
  const handleUserText = useCallback(
    (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return

      setMessages((prev) => [
        ...prev,
        { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
      ])

      // 安全确认检测
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

      // 正常流程：记录输入，等待用户点"整理我想说的"
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
    [],
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
    (id: string, title: string, body: string, isVague: boolean) => {
      if (scope && isActuallySent(scope)) {
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
          text:
            scope && isActuallySent(scope)
              ? '已发送到家长端。家长会看到你确认后的内容，看不到你的原始输入和未分享的部分。'
              : '草稿已保存。这份草稿只有你自己能看到，你可以稍后自己决定怎么发。',
        },
      ])
    },
    [scope, updateMessage],
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
