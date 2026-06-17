// 高风险表达检测
// 命中即跳转安全支持页，不生成普通三张卡，不追问细节，不输出方法。

// 高风险关键词（含常见变体）
const HIGH_RISK_WORDS: string[] = [
  '想死',
  '不想活',
  '不想活了',
  '自杀',
  '自残',
  '伤害自己',
  '伤害别人',
  '结束一切',
  '永远消失',
  '活着没意思',
  '撑不下去',
  '想跳楼',
  '想割腕',
  '寻死',
  '轻生',
  '了结自己',
  '活不下去',
  '撑不住',
  '不想存在',
  '消失算了',
]

// 变体正则：覆盖插入字符、空格等干扰
const HIGH_RISK_PATTERNS: RegExp[] = [
  /想.{0,2}死/,
  /不.{0,2}活/,
  /想.{0,2}跳楼/,
  /想.{0,2}割腕/,
  /结束.{0,2}一切/,
  /活着没.{0,2}意思/,
  /撑不.{0,2}下去/,
  /不想.{0,2}存在/,
]

// 预处理：去空格、转小写、繁简统一
function preprocess(text: string): string {
  return text
    .replace(/\s+/g, '')
    .toLowerCase()
    .replace(/臺/g, '台')
    .replace(/著/g, '着')
}

// 检测输入是否命中高风险表达
export function isHighRisk(input: string): boolean {
  if (!input) return false
  const text = preprocess(input)

  if (HIGH_RISK_WORDS.some((w) => text.includes(preprocess(w)))) {
    return true
  }
  if (HIGH_RISK_PATTERNS.some((p) => p.test(text))) {
    return true
  }
  return false
}
