// 登录/注册面板
// 支持三种身份注册，并提供演示账号快速登录
// 演示账号与后端 seed.py 保持一致：demo_child/demo_parent/demo_teacher，密码 demo123456

import { useState } from 'react'
import type { Identity } from '../types'
import {
  ApiError,
  login,
  register,
  type AuthUser,
} from '../lib/apiClient'

interface LoginPanelProps {
  identity: Identity
  onSuccess: (user: AuthUser) => void
  onBack: () => void
  onSkip: () => void
}

type Mode = 'login' | 'register'

// 演示账号（与后端 seed.py DEMO_USERS 完全一致）
const DEMO_ACCOUNTS: Record<Identity, { username: string; password: string }> = {
  student: { username: 'demo_child', password: 'demo123456' },
  parent: { username: 'demo_parent', password: 'demo123456' },
  teacher: { username: 'demo_teacher', password: 'demo123456' },
}

const IDENTITY_TO_ROLE: Record<Identity, 'child' | 'parent' | 'teacher'> = {
  student: 'child',
  parent: 'parent',
  teacher: 'teacher',
}

const IDENTITY_LABEL: Record<Identity, string> = {
  student: '学生',
  parent: '家长',
  teacher: '老师',
}

export function LoginPanel({ identity, onSuccess, onBack, onSkip }: LoginPanelProps) {
  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const role = IDENTITY_TO_ROLE[identity]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    setLoading(true)
    setError(null)

    try {
      let user: AuthUser
      if (mode === 'register') {
        if (!username.trim() || !password.trim() || !displayName.trim()) {
          throw new ApiError(400, '请填写所有字段')
        }
        user = await register({
          username: username.trim(),
          display_name: displayName.trim(),
          role,
          password: password.trim(),
        })
      } else {
        if (!username.trim() || !password.trim()) {
          throw new ApiError(400, '请填写用户名和密码')
        }
        user = await login({
          username: username.trim(),
          password: password.trim(),
        })
      }
      onSuccess(user)
    } catch (e) {
      const err = e as ApiError
      if (err.status === 0) {
        setError('无法连接后端服务，请确认后端已启动（默认 http://localhost:8000）')
      } else {
        setError(err.detail || '操作失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    if (loading) return
    setLoading(true)
    setError(null)
    try {
      const demo = DEMO_ACCOUNTS[identity]
      const user = await login(demo)
      onSuccess(user)
    } catch (e) {
      const err = e as ApiError
      if (err.status === 0) {
        setError('无法连接后端服务，请确认后端已启动')
      } else {
        setError(`演示账号登录失败：${err.detail}（可点击下方"使用本地模式"继续）`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="app-header">
          <h1 className="app-title">{IDENTITY_LABEL[identity]}登录</h1>
          <p className="app-subtitle">
            {mode === 'login' ? '登录后端账号以使用完整功能' : '注册新账号'}
          </p>
        </header>

        <main className="app-main">
          <form className="login-form" onSubmit={handleSubmit}>
            {mode === 'register' && (
              <div className="form-field">
                <label className="form-label">显示名称</label>
                <input
                  type="text"
                  className="form-input"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="如：小明"
                  maxLength={64}
                  autoComplete="off"
                />
              </div>
            )}

            <div className="form-field">
              <label className="form-label">用户名</label>
              <input
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="3-64 个字符"
                maxLength={64}
                autoComplete="off"
              />
            </div>

            <div className="form-field">
              <label className="form-label">密码</label>
              <input
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="至少 6 位"
                minLength={6}
                autoComplete="off"
              />
            </div>

            {error && <div className="form-error">{error}</div>}

            <button
              type="submit"
              className="primary-btn"
              disabled={loading}
            >
              {loading ? '处理中…' : mode === 'login' ? '登录' : '注册'}
            </button>

            <div className="login-actions">
              <button
                type="button"
                className="ghost-btn"
                onClick={() => {
                  setMode(mode === 'login' ? 'register' : 'login')
                  setError(null)
                }}
              >
                {mode === 'login' ? '没有账号？去注册' : '已有账号？去登录'}
              </button>
              <button
                type="button"
                className="ghost-btn"
                onClick={handleDemoLogin}
                disabled={loading}
              >
                演示账号登录
              </button>
            </div>
          </form>

          <div className="login-divider">
            <span>或者</span>
          </div>

          <button type="button" className="ghost-btn" onClick={onSkip}>
            使用本地模式（不连接后端）
          </button>

          <button type="button" className="ghost-btn" onClick={onBack}>
            返回身份选择
          </button>
        </main>
      </div>
    </div>
  )
}
