// 共享类型定义

export type Identity = 'student' | 'parent' | 'teacher'

// 安全确认分支
export type SafetyChoice = 'safe' | 'unsafe' | null

// 孩子端澄清三区块
export interface ChildClarify {
  wantToSay: string    // 我真正想表达什么
  fear: string         // 我怕什么
  hope: string         // 我希望大人怎么做
}

// 分享范围
export type ShareScope =
  | 'private'        // 只让我自己看看
  | 'self-send'      // 帮我生成一段话，我自己发
  | 'send-parent'    // 帮我发给家长
  | 'vague'          // 只告诉家长一个很模糊的提醒

// 给家长的沟通请求草稿
export interface ParentMessageDraft {
  title: string
  body: string
  isVague: boolean   // 是否为模糊提醒模式
}

// 收件箱消息
export interface InboxMessage {
  id: string
  from: 'child' | 'parent'
  title: string
  body: string
  isVague: boolean
  createdAt: number
  read: boolean
}

// 家长端 AI 建议结果
export interface ParentGuide {
  firewallNote: string   // 防火墙说明
  iceBreaker: string     // 破冰建议
  sayThree: string[]     // 可以说的三句话
  notSayThree: string[]  // 暂时不要说的三句话
  nextStep: string       // 下一步建议
  replyDraft: string     // 回应草稿
}

// 老师端 AI 建议结果
export interface TeacherGuide {
  summary: string         // 非诊断式情况摘要
  privacyNote: string     // 隐私提醒
  talkAdvice: string[]    // 谈话建议
  observePoints: string[] // 观察点
  referAdvice: string     // 转介建议
}

// ===== Chat-first 消息类型 =====

export type ChatMessage =
  | { id: string; role: 'ai'; type: 'text'; text: string }
  | { id: string; role: 'user'; type: 'text'; text: string }
  | {
      id: string
      role: 'ai'
      type: 'clarify-card'
      clarify: ChildClarify
      confirmed: boolean
    }
  | {
      id: string
      role: 'ai'
      type: 'scope-card'
      selected: ShareScope | null
    }
  | {
      id: string
      role: 'ai'
      type: 'draft-card'
      draft: ParentMessageDraft
      scope: ShareScope
      sent: boolean
    }
  | {
      id: string
      role: 'ai'
      type: 'safety-card'
      choice: SafetyChoice
    }
  | {
      id: string
      role: 'ai'
      type: 'inbox-card'
      message: InboxMessage
    }
  | {
      id: string
      role: 'ai'
      type: 'guide-card'
      guide: ParentGuide
      isFirewall?: boolean
      replySent?: boolean
    }
  | {
      id: string
      role: 'ai'
      type: 'teacher-guide-card'
      guide: TeacherGuide
    }

// 孩子端对话阶段（用于上下文感知快捷操作）
export type ChildStage =
  | 'initial'      // 初始，未输入
  | 'input-done'   // 已输入，待整理
  | 'clarify-done' // 已整理，待选分享范围
  | 'scope-done'   // 已选分享范围，待预览
  | 'sent'         // 已发送
  | 'safety'       // 安全确认中

// 家长端对话阶段
export type ParentStage =
  | 'initial'
  | 'guide-shown'

// 老师端对话阶段
export type TeacherStage =
  | 'initial'
  | 'guide-shown'
