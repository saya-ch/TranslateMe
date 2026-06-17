// 示例输入：贴近真实青少年会说的话，不正式、不刻意
export interface Example {
  text: string
  tag: string
}

export const EXAMPLES: Example[] = [
  { text: '我很烦，不想去学校', tag: '疲惫低落' },
  { text: '最近上课总想哭', tag: '疲惫低落' },
  { text: '爸妈只会说我矫情', tag: '亲子冲突' },
  { text: '我想找老师，但怕被同学知道', tag: '老师沟通' },
  { text: '你们不懂我', tag: '亲子冲突' },
  { text: '考试考砸了，不敢回家', tag: '学业压力' },
  { text: '同学都不理我，感觉自己被排挤了', tag: '同伴关系' },
  { text: '我最近真的很累，什么都不想做', tag: '疲惫低落' },
]
