// 后端 API 客户端
// 默认走后端，失败时由调用方 fallback 到本地模拟

const API_BASE =
  (import.meta as unknown as { env?: { VITE_API_BASE?: string } }).env?.VITE_API_BASE ||
  'http://localhost:8000/api/v1'

const TOKEN_KEY = 'family_ai_token'
const USER_KEY = 'family_ai_user'

// ===== Token / 用户信息持久化 =====

export interface AuthUser {
  id: string
  username: string
  display_name: string
  role: 'child' | 'parent' | 'teacher' | 'counselor'
  child_profile_id?: string | null
}

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function getStoredUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? (JSON.parse(raw) as AuthUser) : null
  } catch {
    return null
  }
}

export function setAuth(token: string, user: AuthUser): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  } catch {
    // 忽略 localStorage 不可用
  }
}

export function clearAuth(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {
    // 忽略
  }
}

// ===== 请求封装 =====

export class ApiError extends Error {
  status: number
  detail: string
  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let resp: Response
  try {
    resp = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    })
  } catch {
    // 网络错误（后端未启动）
    throw new ApiError(0, '无法连接到后端服务')
  }

  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`
    try {
      const body = await resp.json()
      detail = body.detail || body.message || detail
    } catch {
      // 忽略 JSON 解析失败
    }
    throw new ApiError(resp.status, detail)
  }

  if (resp.status === 204) {
    return undefined as T
  }
  return (await resp.json()) as T
}

// ===== 认证 =====

export interface RegisterParams {
  username: string
  display_name: string
  role: 'child' | 'parent' | 'teacher' | 'counselor'
  password: string
}

export interface LoginParams {
  username: string
  password: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface MeResponse {
  user: {
    id: string
    username: string
    display_name: string
    role: string
  }
  child_profiles: Array<{ id: string }>
}

export async function register(params: RegisterParams): Promise<AuthUser> {
  const token = await request<TokenResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(params),
  })

  // 临时存 token，再拉取用户信息
  try {
    localStorage.setItem(TOKEN_KEY, token.access_token)
  } catch {
    // 忽略
  }
  return await fetchMe()
}

export async function login(params: LoginParams): Promise<AuthUser> {
  const token = await request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(params),
  })

  try {
    localStorage.setItem(TOKEN_KEY, token.access_token)
  } catch {
    // 忽略
  }
  return await fetchMe()
}

export async function fetchMe(): Promise<AuthUser> {
  const me = await request<MeResponse>('/auth/me', { method: 'GET' })
  const user: AuthUser = {
    id: me.user.id,
    username: me.user.username,
    display_name: me.user.display_name,
    role: me.user.role as AuthUser['role'],
    child_profile_id: me.child_profiles?.[0]?.id || null,
  }
  const token = getToken()
  if (token) {
    setAuth(token, user)
  }
  return user
}

// ===== 家庭组 =====

export interface FamilyGroupParams {
  child_user_id: string
  guardian_user_id: string
}

export async function createFamilyGroup(
  params: FamilyGroupParams,
): Promise<{ group_id: string; child_id: string; members: unknown[] }> {
  return await request('/family/groups', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ===== 可访问的孩子列表 =====

export interface AccessibleChild {
  child_id: string
  user_id: string
  display_name: string
  age_group: string
  grade: string
  username: string | null
}

export async function listAccessibleChildren(): Promise<AccessibleChild[]> {
  const resp = await request<{ items: AccessibleChild[]; total: number }>(
    '/family/children',
    { method: 'GET' },
  )
  return resp.items
}

// ===== 会话 / 聊天 =====

export interface ChatParams {
  conversation_id?: string | null
  child_id: string
  text: string
}

export interface ChatResult {
  message_id: string
  conversation_id: string
  needs_safety_check: boolean
  safety_event_id?: string | null
  draft: {
    draft_id: string
    title: string
    body: string
    level: number
    scope: string
    source: string
  } | null
  source: string
}

export async function sendChildMessage(
  params: ChatParams,
): Promise<ChatResult> {
  return await request('/conversations/chat', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ===== 草稿确认（支持孩子确认后的最终 title/body）=====

export interface DraftConfirmParams {
  draft_id: string
  to_role: string
  level: number
  title?: string
  body?: string
}

export interface DraftConfirmResult {
  share_id: string
  inbox_message_id: string
  delivered_to: string
  title: string
  body: string
}

export async function confirmDraft(
  params: DraftConfirmParams,
): Promise<DraftConfirmResult> {
  return await request(`/conversations/drafts/${params.draft_id}/confirm`, {
    method: 'POST',
    body: JSON.stringify({
      to_role: params.to_role,
      level: params.level,
      title: params.title,
      body: params.body,
    }),
  })
}

// ===== 收件箱 =====

export interface InboxItemDTO {
  id: string
  child_id: string
  from_role: string
  title: string
  body: string
  level: number
  read: boolean
  delivered_at: string
  status: string
}

export async function fetchInbox(
  child_id?: string,
): Promise<InboxItemDTO[]> {
  const qs = child_id ? `?child_id=${encodeURIComponent(child_id)}` : ''
  const resp = await request<{ items: InboxItemDTO[]; total: number }>(
    `/conversations/inbox${qs}`,
    { method: 'GET' },
  )
  return resp.items
}

// ===== 家长回复 =====

export interface ReplyParams {
  child_id: string
  to_role: string
  body: string
  source_inbox_id?: string | null
}

export async function replyToChild(
  params: ReplyParams,
): Promise<{ reply_id: string; inbox_message_id: string }> {
  return await request('/conversations/reply', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ===== LLM 家长提问 =====

export interface ParentAskParams {
  child_id: string
  question: string
}

export interface ParentAskResult {
  source: string
  is_probing: boolean
  content: {
    firewall_note?: string
    icebreaker?: string
    say_three?: string[]
    not_say_three?: string[]
    next_step?: string
    reply_draft?: string
    _note?: string
  }
}

export async function parentAsk(
  params: ParentAskParams,
): Promise<ParentAskResult> {
  return await request('/llm/parent-ask', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ===== LLM 老师提问 =====

export interface TeacherAskParams {
  child_id: string
  observation: string
}

export interface TeacherAskResult {
  source: string
  content: {
    summary?: string
    privacy_note?: string
    talk_advice?: string[]
    observe_points?: string[]
    referral_advice?: string
  }
}

export async function teacherAsk(
  params: TeacherAskParams,
): Promise<TeacherAskResult> {
  return await request('/llm/teacher-ask', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// ===== 安全事件 =====

export interface SafetyResolveParams {
  event_id: string
  branch: 'safe_continue' | 'unsafe_support' | 'escalation'
}

export interface SafetyResolveResult {
  resolved_at: string | null
  resources_shown: boolean
  llm_called: boolean
  message: string
}

export async function resolveSafetyEvent(
  params: SafetyResolveParams,
): Promise<SafetyResolveResult> {
  return await request(`/safety/events/${params.event_id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ branch: params.branch }),
  })
}

// ===== 健康检查 =====

export async function pingBackend(): Promise<boolean> {
  try {
    const resp = await fetch('http://localhost:8000/health')
    return resp.ok
  } catch {
    return false
  }
}
