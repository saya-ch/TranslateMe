// 孩子端：澄清三区块 + 给家长的沟通请求草稿生成
// 严格遵守：不替孩子判断问题，只帮孩子澄清自己愿意表达的内容。
// 所有对外消息均为可编辑草稿，确认后才分享。

import type { ChildClarify, ParentMessageDraft, ShareScope } from '../types'

// 基于原始倾诉，生成澄清三区块的初始草稿（孩子可编辑）
export function buildClarifyDraft(rawInput: string): ChildClarify {
  const trimmed = rawInput.trim().slice(0, 120)
  return {
    wantToSay: trimmed || '我想说……',
    fear: '我担心说出来会被评价，或者被觉得矫情。',
    hope: '我希望大人能先听我说完，不急着评价。',
  }
}

// 根据分享范围 + 澄清内容，生成给家长的沟通请求草稿
export function buildParentMessageDraft(
  clarify: ChildClarify,
  scope: ShareScope,
): ParentMessageDraft {
  // 模糊提醒模式：只告诉家长"孩子想聊聊"，不透露具体内容
  if (scope === 'vague') {
    return {
      title: '孩子想跟你聊聊',
      body: '孩子通过帮我说出口发来一个提醒：ta 最近有些事想跟你说，但还没准备好讲细节。建议你先表达愿意听，不追问原因。',
      isVague: true,
    }
  }

  // 其他三种范围都生成可编辑草稿（private/self-send 不实际发送，但草稿仍生成供预览）
  const wantPart = clarify.wantToSay.trim() || '我最近有些事想说'
  const hopePart = clarify.hope.trim() || '希望你能先听我说完'

  const body = `孩子想跟你说一些最近的事。\n\nta 想表达的是：${wantPart}\n\nta 希望你能：${hopePart}\n\n建议你找一个不被打扰的时间，先听 ta 说完，不急着评价。`

  return {
    title: '孩子通过帮我说出口发来一条沟通请求',
    body,
    isVague: false,
  }
}

// 判断分享范围是否实际发送到家长端
export function isActuallySent(scope: ShareScope): boolean {
  return scope === 'send-parent' || scope === 'vague'
}
