// 共享类型定义

export type Identity = 'student' | 'parent' | 'teacher'

export type Scene = 'tell-parent' | 'tell-teacher' | 'sort-out' | 'urgent'

export type Step = 'home' | 'identity' | 'scene' | 'input' | 'result' | 'safety'

export interface PressureSource {
  key: string
  label: string
}

export interface SelfCard {
  restate: string
  sendable: string
  nextStep: string
}

export interface ParentCard {
  understand: string
  sayThree: string[]
  notSayThree: string[]
  nextStep: string
}

export interface TeacherCard {
  summary: string
  talkAdvice: string[]
  observePoints: string[]
  referAdvice: string
}

export interface ActionCards {
  self: SelfCard
  parent: ParentCard
  teacher: TeacherCard
  sources: PressureSource[]
}
