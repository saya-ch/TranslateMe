// 本地模拟收件箱与会话存储
// Demo 阶段用模块级内存状态模拟三方收件箱，同一设备切换身份即可看到消息流。
// 真实产品需要后端会话存储 + 权限控制 + 分享授权记录。

import type { InboxMessage } from '../types'

// 模块级内存状态（刷新即销毁，符合隐私最小化）
const parentInbox: InboxMessage[] = []
const childInbox: InboxMessage[] = []

// 简单订阅
type Listener = () => void
const listeners = new Set<Listener>()

function notify() {
  listeners.forEach((l) => l())
}

export function subscribe(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

// 家长端收件箱
export function getParentInbox(): InboxMessage[] {
  return [...parentInbox]
}

// 孩子端收件箱
export function getChildInbox(): InboxMessage[] {
  return [...childInbox]
}

// 孩子发送沟通请求到家长端
export function childSendMessageToParent(msg: Omit<InboxMessage, 'id' | 'createdAt' | 'read' | 'from'>): void {
  parentInbox.unshift({
    ...msg,
    id: `m-${Date.now()}`,
    from: 'child',
    createdAt: Date.now(),
    read: false,
  })
  notify()
}

// 家长回复到孩子端
export function parentSendReplyToChild(msg: Omit<InboxMessage, 'id' | 'createdAt' | 'read' | 'from'>): void {
  childInbox.unshift({
    ...msg,
    id: `r-${Date.now()}`,
    from: 'parent',
    createdAt: Date.now(),
    read: false,
  })
  notify()
}

// 标记已读
export function markRead(id: string): void {
  const inParent = parentInbox.find((m) => m.id === id)
  if (inParent) inParent.read = true
  const inChild = childInbox.find((m) => m.id === id)
  if (inChild) inChild.read = true
  notify()
}

// 清空（演示重置）
export function clearAll(): void {
  parentInbox.length = 0
  childInbox.length = 0
  notify()
}

// 预置演示消息（方便评委快速看到家长端效果）
export function loadDemoMessages(): void {
  clearAll()
  parentInbox.unshift({
    id: 'demo-child-1',
    from: 'child',
    title: '孩子通过帮我说出口发来一条沟通请求',
    body: '孩子想跟你说一些最近的事。ta 希望你能先听 ta 说完，不急着评价。建议你找一个不被打扰的时间，比如饭后 10 分钟。',
    isVague: false,
    createdAt: Date.now() - 1000 * 60 * 5,
    read: false,
  })
  childInbox.unshift({
    id: 'demo-parent-1',
    from: 'parent',
    title: '家长通过帮我说出口发来一条回应',
    body: '我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲十分钟。',
    isVague: false,
    createdAt: Date.now() - 1000 * 60 * 3,
    read: false,
  })
  notify()
}
