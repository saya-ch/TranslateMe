// 孩子端：澄清三区块 + 给家长的沟通请求草稿生成
// 严格遵守：不替孩子判断问题，只帮孩子澄清自己愿意表达的内容。
// 隐私边界：send-parent 默认草稿必须是降敏摘要，不直接包含孩子原始输入。
// 只有孩子在预览卡里主动编辑加入的内容，才会被发送给家长。

import type { ChildClarify, ParentMessageDraft, ShareScope } from '../types'

// 基于原始倾诉，生成澄清三区块的初始草稿（孩子可编辑）
// 注意：澄清内容默认仅孩子可见，不进入对外消息
export function buildClarifyDraft(rawInput: string): ChildClarify {
  const trimmed = rawInput.trim().slice(0, 120)
  return {
    wantToSay: trimmed || '我想说……',
    fear: '我担心说出来会被评价，或者被觉得矫情。',
    hope: '我希望大人能先听我说完，不急着评价。',
  }
}

// send-parent 默认降敏摘要（不包含孩子原始输入）
const SEND_PARENT_DEFAULT_BODY =
  '孩子最近有些事想跟你说，ta 希望你能先听完，不急着评价。建议你找一个不被打扰的时间，先用十分钟听 ta 说。'

// vague 模式默认文案（只告诉家长"孩子想聊聊"，不透露具体内容）
const VAGUE_DEFAULT_BODY =
  '孩子通过帮我说出口发来一个提醒：ta 最近有些事想跟你说，但还没准备好讲细节。建议你先表达愿意听，不追问原因。'

// 根据分享范围 + 澄清内容，生成给家长的沟通请求草稿
// 关键：默认永远是降敏摘要，不直接包含孩子原始输入
export function buildParentMessageDraft(
  _clarify: ChildClarify,
  scope: ShareScope,
): ParentMessageDraft {
  // 模糊提醒模式：只告诉家长"孩子想聊聊"，不透露具体内容
  if (scope === 'vague') {
    return {
      title: '孩子想跟你聊聊',
      body: VAGUE_DEFAULT_BODY,
      isVague: true,
    }
  }

  // send-parent 模式：默认降敏摘要，不包含孩子原始输入
  // 如果孩子想加入具体内容，由孩子在预览卡里主动编辑加入
  if (scope === 'send-parent') {
    return {
      title: '孩子通过帮我说出口发来一条沟通请求',
      body: SEND_PARENT_DEFAULT_BODY,
      isVague: false,
    }
  }

  // private / self-send 模式：草稿仅孩子可见，仍默认降敏
  // 孩子可自行编辑，但不会自动发送
  return {
    title: '孩子通过帮我说出口整理了一段话',
    body: SEND_PARENT_DEFAULT_BODY,
    isVague: false,
  }
}

// 判断分享范围是否实际发送到家长端
export function isActuallySent(scope: ShareScope): boolean {
  return scope === 'send-parent' || scope === 'vague'
}
