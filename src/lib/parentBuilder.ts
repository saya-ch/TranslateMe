// 家长端：通用沟通建议 + 信息防火墙
// 严格遵守：AI 不能透露孩子未授权的具体事实。
// 严格追问检测：只要问题里同时出现"孩子"和具体追问词，就触发防火墙拒绝卡。

import type { ParentGuide } from '../types'

// 追问触发词（与"孩子/儿子/女儿"同时出现即触发防火墙）
const PROBING_KEYWORDS = [
  '原话',
  '具体内容',
  '具体细节',
  '详细内容',
  '详细细节',
  '说了什么',
  '跟你说什么',
  '跟你聊了什么',
  '发生了什么',
  '经历了什么',
  '什么事',
  '怎么回事',
  '到底怎么了',
  '真正原因',
  '真实原因',
  '告诉我具体',
  '告诉我内容',
  '告诉我细节',
  '告诉我原话',
  '透露',
]

const SUBJECT_KEYWORDS = ['孩子', '儿子', '女儿', '他', '她', 'ta']

// 检测家长是否在追问孩子未授权的具体内容
// 规则：问题里同时出现孩子指代和明确索要原话/细节的词，即触发
export function isProbingQuestion(question: string): boolean {
  const text = question.replace(/\s+/g, '').toLowerCase()
  if (!SUBJECT_KEYWORDS.some((kw) => text.includes(kw))) return false
  return PROBING_KEYWORDS.some((kw) => text.includes(kw))
}

// 通用沟通建议（不依赖孩子具体内容）
function buildGenericGuide(): ParentGuide {
  return {
    firewallNote:
      '我不能透露孩子没有允许分享的内容。以下建议是基于通用沟通方式给出的，不涉及孩子具体说了什么。',
    iceBreaker:
      '先不要追问具体原因，可以先表达你愿意听。比如找一个不被打扰的时间，说一句："我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲十分钟。"',
    sayThree: [
      '我先听你说完，不急着评价。',
      '你说的我都记下了，谢谢你愿意告诉我。',
      '我们慢慢来，不用一次说完。',
    ],
    notSayThree: [
      '别想那么多，没什么大不了的。',
      '别人家孩子不也好好的吗。',
      '你就是太矫情/太懒了。',
    ],
    nextStep:
      '先听孩子说完，约定一个不被打扰的谈话时间；观察接下来几天的状态；如果持续低落或提到伤害自己，联系学校心理老师或专业人员。',
    replyDraft:
      '我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲十分钟。什么时候方便都可以，我等你。',
  }
}

// 防火墙拒绝时的建议（追问孩子具体内容时使用）
function buildFirewallGuide(): ParentGuide {
  return {
    firewallNote:
      '我注意到你在问孩子具体说了什么。未经孩子同意，我不能透露具体内容，也不能暗示孩子经历了什么。但我可以帮你想想怎么让 ta 愿意开口。',
    iceBreaker:
      '与其追问原因，不如先表达你愿意听。孩子愿意开口需要安全感，追问反而可能让 ta 闭嘴。可以先说："我不会逼你说，但我想让你知道，你什么时候想说都可以。"',
    sayThree: [
      '我不会逼你说，但我想让你知道，你什么时候想说都可以。',
      '你不用一次说完，慢慢来。',
      '不管是什么事，我都愿意先听。',
    ],
    notSayThree: [
      '你到底怎么了，告诉我。',
      '你是不是遇到了什么事，快说。',
      '别瞒着我，我知道你肯定有事。',
    ],
    nextStep:
      '先表达愿意听、不追问；给孩子空间和时间；如果孩子持续不愿沟通且状态低落，可联系学校心理老师。',
    replyDraft:
      '我不会逼你说，但我想让你知道，你什么时候想说都可以。不用一次说完，慢慢来，我等你。',
  }
}

// 根据家长提问生成建议（含防火墙检测）
export function buildParentGuide(question: string): ParentGuide {
  if (isProbingQuestion(question)) {
    return buildFirewallGuide()
  }
  return buildGenericGuide()
}

// 防火墙拒绝纯文本（用于聊天中的拒绝卡）
export function firewallRefuseText(): string {
  return '抱歉，未经孩子同意，我不能透露具体内容，也不能暗示孩子经历了什么。但我可以帮你想想怎么让 ta 愿意开口。比如可以先表达你愿意听，不追问原因。'
}
