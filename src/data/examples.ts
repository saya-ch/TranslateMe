// 示例输入：贴近真实青少年会说的话

export interface Example {
  text: string
  tag: string
}

// 孩子端示例
export const CHILD_EXAMPLES: Example[] = [
  { text: '我很烦，不想去学校', tag: '疲惫低落' },
  { text: '最近上课总想哭', tag: '疲惫低落' },
  { text: '爸妈只会说我矫情', tag: '亲子冲突' },
  { text: '我想找老师，但怕被同学知道', tag: '老师沟通' },
  { text: '你们不懂我', tag: '亲子冲突' },
  { text: '考试考砸了，不敢回家', tag: '学业压力' },
  { text: '同学都不理我，感觉自己被排挤了', tag: '同伴关系' },
  { text: '我最近真的很累，什么都不想做', tag: '疲惫低落' },
]

// 家长端示例提问
export const PARENT_EXAMPLES: Example[] = [
  { text: '孩子最近为什么闷闷不乐，不愿意说话？', tag: '理解孩子' },
  { text: '我该怎么开口跟孩子聊？', tag: '怎么开口' },
  { text: '孩子不愿意跟我说怎么办？', tag: '沟通受阻' },
  { text: '我是不是说错话了？', tag: '自我反思' },
]

// 老师端示例观察
export const TEACHER_EXAMPLES: Example[] = [
  { text: '学生最近上课走神，作业也不交', tag: '课堂表现' },
  { text: '学生下课总一个人待着，不和同学玩', tag: '同伴关系' },
  { text: '学生最近请假变多了', tag: '到校情况' },
  { text: '学生成绩突然下滑明显', tag: '学业变化' },
]
