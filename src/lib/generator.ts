// 非诊断式卡片生成逻辑
// 使用本地规则和模板模拟受控 AI 转译，不调用 LLM。
// 严格遵守：不诊断、不输出病名、不输出严重程度、不承诺治愈、输出具体可行动。

import type {
  ActionCards,
  Identity,
  ParentCard,
  PressureSource,
  Scene,
  SelfCard,
  TeacherCard,
} from '../types'

// 压力来源关键词表
const PRESSURE_KEYWORDS: Record<string, { label: string; words: string[] }> = {
  academic: {
    label: '学业压力',
    words: ['考试', '作业', '成绩', '排名', '补课', '考砸', '分数', '刷题', '测验', '月考', '期中', '期末', '没考好'],
  },
  parent: {
    label: '亲子冲突',
    words: ['爸妈', '父母', '家长', '被骂', '矫情', '比较', '妈妈', '爸爸', '骂我', '嫌我', '唠叨', '管我', '不懂我'],
  },
  peer: {
    label: '同伴关系',
    words: ['同学', '朋友', '排挤', '孤立', '欺负', '嘲笑', '没人理', '不合群', '小团体', '被说', '不理我'],
  },
  teacher: {
    label: '老师沟通',
    words: ['老师', '班主任', '上课', '找老师', '怕同学知道', '被点名', '批评', '办公室'],
  },
  fatigue: {
    label: '疲惫低落',
    words: ['很累', '烦', '不想去学校', '不想说', '想哭', '没力气', '累', '烦人', '没意思', '提不起劲', '撑不住', '不想动'],
  },
  privacy: {
    label: '隐私担忧',
    words: ['怕别人知道', '别告诉同学', '不想公开', '怕被知道', '丢人', '不好意思说', '怕知道'],
  },
}

// 识别输入中的压力来源
export function detectSources(input: string): PressureSource[] {
  const sources: PressureSource[] = []
  for (const [key, info] of Object.entries(PRESSURE_KEYWORDS)) {
    if (info.words.some((w) => input.includes(w))) {
      sources.push({ key, label: info.label })
    }
  }
  return sources
}

// 截断过长输入，避免卡片溢出
function trimInput(input: string): string {
  const trimmed = input.trim().slice(0, 120)
  return trimmed.length < input.trim().length ? `${trimmed}…` : trimmed
}

// 根据压力来源生成“给自己的卡”
function generateSelfCard(_input: string, sources: PressureSource[]): SelfCard {
  const keys = sources.map((s) => s.key)
  const hasAcademic = keys.includes('academic')
  const hasParent = keys.includes('parent')
  const hasPeer = keys.includes('peer')
  const hasFatigue = keys.includes('fatigue')
  const hasPrivacy = keys.includes('privacy')

  // 复述：低压力语言，不诊断
  let restate = '你说的这句话，可能是在表达最近有些事让你觉得吃力。'
  if (hasAcademic && hasParent) {
    restate = '你说的可能是，学业上的压力和家里人的反应，让你觉得有点喘不过气。'
  } else if (hasAcademic) {
    restate = '你说的可能是，最近学习上的事让你觉得压力有点大。'
  } else if (hasParent) {
    restate = '你说的可能是，和爸妈之间的沟通让你觉得不被理解。'
  } else if (hasPeer) {
    restate = '你说的可能是，和同学相处时你觉得被孤立或受伤了。'
  } else if (hasFatigue) {
    restate = '你说的可能是，你最近真的很累，需要缓一缓。'
  } else if (hasPrivacy) {
    restate = '你说的可能是，有些事你想说，但又担心被别人知道。'
  }

  // 可发送句：可以直接发出去的话
  let sendable = '我最近状态不太好，想跟你说一下，可能说得有点乱。'
  if (hasAcademic) {
    sendable = '我最近学习压力有点大，想先跟你说一下，不用马上解决。'
  } else if (hasParent) {
    sendable = '我有些话想跟你说，希望你能先听我说完，不急着评价。'
  } else if (hasPeer) {
    sendable = '我最近和同学之间有点事，想找个时间跟你说一下。'
  } else if (hasPrivacy) {
    sendable = '我有件事想跟你说，但希望先不要告诉别人，可以吗？'
  }

  // 小下一步
  let nextStep = '可以先约一个不被打扰的 10 分钟，用文字或者当面说都行。'
  if (hasPrivacy) {
    nextStep = '可以先用文字发出去，不一定当面说；也可以先只告诉一个你信任的人。'
  } else if (hasFatigue) {
    nextStep = '可以先只说一件最具体的事，不用一次说完。'
  }

  return { restate, sendable, nextStep }
}

// 根据压力来源生成“给家长的卡”
function generateParentCard(_input: string, sources: PressureSource[]): ParentCard {
  const keys = sources.map((s) => s.key)
  const hasAcademic = keys.includes('academic')
  const hasPeer = keys.includes('peer')
  const hasFatigue = keys.includes('fatigue')
  const hasPrivacy = keys.includes('privacy')

  // 理解：帮家长看懂孩子这句话背后可能在表达什么
  let understand = '孩子愿意把这句话说出来，本身就是在发出信号。这句话背后可能是压力、疲惫、害怕或无助，而不是偷懒或叛逆。'
  if (hasAcademic) {
    understand = '孩子提到学业相关的事，可能是在表达学习压力已经让他有些吃力，而不是不想努力。'
  } else if (hasPeer) {
    understand = '孩子提到同学相关的事，可能是在同伴关系里受了伤，需要被接住，而不是被说“别理他们就行”。'
  } else if (hasFatigue) {
    understand = '孩子说累、烦、不想去学校，可能是真的撑不住了，需要先被听见，而不是被催着振作。'
  }

  // 可以说的三句话
  const sayThree: string[] = [
    '我先听你说完，不急着评价。',
    '你说的我都记下了，谢谢你愿意告诉我。',
    '我们慢慢来，不用一次说完。',
  ]

  // 暂时不要说的三句话
  const notSayThree: string[] = [
    '别想那么多，没什么大不了的。',
    '别人家孩子不也好好的吗。',
    '你就是太矫情/太懒了。',
  ]

  // 下一步建议
  let nextStep = '先听孩子说完，约定一个不被打扰的谈话时间；观察接下来几天的状态；如果持续低落或提到伤害自己，联系学校心理老师或专业人员。'
  if (hasPrivacy) {
    nextStep = '先承诺不扩大范围，让孩子知道你不会立刻告诉老师或其他家长；约定一个只属于你们俩的谈话时间；必要时再一起商量是否联系学校心理老师。'
  }

  return { understand, sayThree, notSayThree, nextStep }
}

// 根据压力来源生成“给老师的卡”
function generateTeacherCard(_input: string, sources: PressureSource[]): TeacherCard {
  const keys = sources.map((s) => s.key)
  const hasAcademic = keys.includes('academic')
  const hasPeer = keys.includes('peer')
  const hasFatigue = keys.includes('fatigue')

  // 非诊断式情况摘要
  let summary = '学生近期可能正在经历一些压力，表现出需要被关注但尚未明确表达的信号。这不是诊断，而是一个值得留意的提示。'
  if (hasAcademic) {
    summary = '学生近期可能在学业方面承受压力，表现出回避或情绪波动，值得关注但不建议直接下判断。'
  } else if (hasPeer) {
    summary = '学生近期可能在同伴关系中遇到困难，有被孤立或受伤的迹象，建议留意但不公开化处理。'
  } else if (hasFatigue) {
    summary = '学生近期可能处于疲惫或低落状态，到校情况和课堂表现值得观察。'
  }

  // 第一次谈话建议
  const talkAdvice: string[] = [
    '找一个不会被同学听见的时间，比如课后单独留一两分钟。',
    '先听学生说完，不打断、不公开化、不当众询问。',
    '不要在班级里提及这次谈话，保护隐私。',
  ]

  // 观察点
  const observePoints: string[] = [
    '这种状态持续了多久，是偶尔还是持续。',
    '到校情况、是否请假、是否回避特定课程。',
    '睡眠和精神状态是否明显变化。',
    '同伴关系是否有异常，是否被孤立。',
    '学业压力是否突然加重。',
    '和家庭沟通的情况（如学生提及）。',
  ]

  // 转介建议
  const referAdvice = '如果这种状态持续出现，或者学生提到伤害自己、不想活等表达，请联系学校心理老师、家长或专业支持渠道；不要独自承担判断责任。'

  return { summary, talkAdvice, observePoints, referAdvice }
}

// 主生成函数：根据身份、场景、输入生成三张行动卡
export function generateCards(
  input: string,
  _identity: Identity,
  _scene: Scene,
): ActionCards {
  const trimmed = trimInput(input)
  const sources = detectSources(trimmed)

  return {
    self: generateSelfCard(trimmed, sources),
    parent: generateParentCard(trimmed, sources),
    teacher: generateTeacherCard(trimmed, sources),
    sources,
  }
}

// 把单张卡转成可复制的纯文本
export function cardToText(card: ActionCards, which: 'self' | 'parent' | 'teacher'): string {
  if (which === 'self') {
    const c = card.self
    return `【给自己的卡】\n\n可能你想说的是：\n${c.restate}\n\n一句可以直接发出去的话：\n${c.sendable}\n\n一个很小的下一步：\n${c.nextStep}`
  }
  if (which === 'parent') {
    const c = card.parent
    return `【给家长的卡】\n\n孩子这句话可能在表达：\n${c.understand}\n\n可以说的三句话：\n${c.sayThree.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n暂时不要说的三句话：\n${c.notSayThree.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n下一步建议：\n${c.nextStep}`
  }
  const c = card.teacher
  return `【给老师的卡】\n\n情况摘要：\n${c.summary}\n\n第一次谈话建议：\n${c.talkAdvice.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n观察点：\n${c.observePoints.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n转介建议：\n${c.referAdvice}`
}
