// 老师端对话控制器

import { useCallback, useMemo, useState } from 'react'
import type { ChatMessage, TeacherStage } from '../types'
import { buildTeacherGuide } from '../lib/teacherBuilder'
import { nextId } from '../components/chat/ChatMessageList'

const AI_GREETING =
  '你好。你可以在这里记录观察到的学生情况，只有你自己能看到。我会帮你整理成谈话建议、观察点和转介建议。'

export function useTeacherController() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: nextId('ai'), role: 'ai', type: 'text', text: AI_GREETING },
  ])
  const [stage, setStage] = useState<TeacherStage>('initial')
  const [lastObservation, setLastObservation] = useState('')

  // 用户发送文本（老师观察记录）
  const handleUserText = useCallback(
    (text: string) => {
      const trimmed = text.trim()
      if (!trimmed) return

      setLastObservation(trimmed)
      setMessages((prev) => [
        ...prev,
        { id: nextId('user'), role: 'user', type: 'text', text: trimmed },
      ])

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
    [],
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
