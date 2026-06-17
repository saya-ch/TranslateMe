// 共享类型定义

export type Identity = 'student' | 'parent' | 'teacher'

// 孩子端步骤
export type ChildStep =
  | 'input'        // 私密倾诉
  | 'safety'       // 安全确认
  | 'clarify'      // 三区块澄清
  | 'scope'        // 分享范围
  | 'preview'      // 草稿预览
  | 'sent'         // 已发送
  | 'inbox'        // 收件箱

// 家长端步骤
export type ParentStep =
  | 'inbox'        // 收件箱
  | 'message'      // 查看孩子沟通请求
  | 'ask'          // 家长提问
  | 'guide'        // AI 通用建议
  | 'reply'        // 回应草稿预览
  | 'replied'      // 已回复

// 老师端步骤
export type TeacherStep =
  | 'input'        // 观察记录
  | 'guide'        // 谈话建议+观察点+转介
  | 'action'       // 选择行动

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

// 家长回应草稿
export interface ParentReplyDraft {
  body: string
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
