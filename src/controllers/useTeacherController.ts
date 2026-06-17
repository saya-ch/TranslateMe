// 老师端对话控制器
// 默认走后端 API，失败时回退到本地模拟

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { ChatMessage, TeacherStage } from '../types'
import { buildTeacherGuide } from '../lib/teacherBuilder'
import { nextId } from '../components/chat/ChatMessageList'
import {
  ApiError,
  listAccessibleChildren,
  teacherAsk,
  type AuthUser,
} from '../lib/apiClient'

const AI_GREETING =
  '你好。你可以在这里记录观察到的学生情况，只有你自己能看到。我会帮你整理成谈话建议、观察点和转介建议。'

interface ControllerProps {
  authUser: AuthUser | null
  useLocalMode: boolean
}

export function useTeacherController({ authUser, useLocalMode }: ControllerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<TeacherStage>('initial')
  const [lastObservation, setLastObservation] = useState('')

  // 当前选中的 child_id
  const childIdRef = useRef<string | null>(null)

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
        }
      } catch (e) {
        const err = e as ApiError
        console.warn('[teacher] 拉取可访问孩子列表失败:', err.detail)
      }
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canUseBackend])

  // 用户发送文本（老师观察记录）
  const handleUserText = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return

      setLastObservation(trimmed)
      setMessages((prev) => [
        ...prev,
        { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
      ])

      // 后端模式：调用 /llm/teacher-ask
      if (canUseBackend && childIdRef.current) {
        try {
          const result = await teacherAsk({
            child_id: childIdRef.current,
            observation: trimmed,
          })
          const c = result.content
          const guide = {
            summary: c.summary,
            privacyNote: c.privacy_note,
            talkAdvice: c.talk_advice || [],
            observePoints: c.observe_points || [],
            referAdvice: c.referral_advice,
          }
          setMessages((prev) => [
            ...prev,
            {
              id: nextId('ai'),
              role: 'ai',
              type: 'teacher-guide-card',
              guide,
            },
          ])
          setStage('guide-shown')
          return
        } catch (e) {
          const err = e as ApiError
          console.warn('[teacher] 后端 teacher-ask 失败，回退本地:', err.detail)
          // 继续走本地流程
        }
      }

      // 本地模式
      const guide = buildTeacherGuide(trimmed)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'teacher-guide-card',
          guide,
        },
      ])
      setStage('guide-shown')
    },
    [canUseBackend],
  )

  // 重新整理建议（基于上次观察）
  const triggerRegenerate = useCallback(() => {
    if (!lastObservation) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId('ai'),
          role: 'ai',
          type: 'text',
          text: '你还没记录观察。先在输入框写一句你看到的情况吧。',
        },
      ])
      return
    }
    const guide = buildTeacherGuide(lastObservation)
    setMessages((prev) => [
      ...prev,
      {
        id: nextId('ai'),
        role: 'ai',
        type: 'teacher-guide-card',
        guide,
      },
    ])
  }, [lastObservation])

  const quickActions = useMemo(() => {
    if (stage === 'guide-shown') {
      return [
        { key: 'regen', label: '重新整理建议', onClick: triggerRegenerate },
      ]
    }
    return []
  }, [stage, triggerRegenerate])

  return {
    messages,
    stage,
    quickActions,
    handleUserText,
  }
}
