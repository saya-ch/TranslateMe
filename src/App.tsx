import { useState } from 'react'
import type { Identity } from './types'
import { IdentitySelect } from './components/IdentitySelect'
import { Footer } from './components/Footer'
import { ChatShell } from './components/chat/ChatShell'
import { useChildController } from './controllers/useChildController'
import { useParentController } from './controllers/useParentController'
import { useTeacherController } from './controllers/useTeacherController'

type Phase = 'home' | 'identity' | 'chat'

export default function App() {
  const [phase, setPhase] = useState<Phase>('home')
  const [identity, setIdentity] = useState<Identity | null>(null)

  // 三个 controller 只在对应身份激活时使用
  const child = useChildController()
  const parent = useParentController()
  const teacher = useTeacherController()

  const handleIdentity = (v: Identity) => {
    setIdentity(v)
    setPhase('chat')
  }

  const handleSwitchIdentity = () => {
    setIdentity(null)
    setPhase('identity')
  }

  const handleReset = () => {
    setIdentity(null)
    setPhase('home')
  }

  if (phase === 'home') {
    return (
      <div className="app-shell">
        <div className="app-container">
          <header className="app-header">
            <h1 className="app-title">帮我说出口</h1>
            <p className="app-subtitle">
              一个围绕你建立的私密沟通中枢。AI 可以分别听见你、家长、老师的想法，但不会自动泄露任何一方原话。
            </p>
          </header>

          <main className="app-main">
            <div className="home-block">
              <p className="home-intro">
                很多时候不是不想求助，而是不知道怎么开口，也怕一开口就被评价。
                <br />
                在这里，你说的内容默认只有你自己能看到。AI 帮你整理成愿意分享的样子，由你决定要不要发、发什么、发多详细。
              </p>
              <div className="home-safe-note">
                如果你现在情况比较紧急，可以选择"我是学生"后直接表达，系统会先做安全确认。
              </div>
              <button
                type="button"
                className="primary-btn"
                onClick={() => setPhase('identity')}
              >
                开始
              </button>
            </div>
          </main>

          <Footer />
        </div>
      </div>
    )
  }

  if (phase === 'identity') {
    return (
      <div className="app-shell">
        <div className="app-container">
          <header className="app-header">
            <h1 className="app-title">你是谁？</h1>
            <p className="app-subtitle">选择身份后进入对话</p>
          </header>

          <main className="app-main">
            <IdentitySelect value={identity} onChange={handleIdentity} />
            <button type="button" className="ghost-btn" onClick={handleReset}>
              返回首页
            </button>
          </main>

          <Footer />
        </div>
      </div>
    )
  }

  // phase === 'chat'
  if (identity === 'student') {
    return (
      <ChatShell
        identity="student"
        messages={child.messages}
        quickActions={child.quickActions}
        inputPlaceholder="说一句你现在最想说的…"
        onSendText={child.handleUserText}
        onSwitchIdentity={handleSwitchIdentity}
        onClarifyConfirm={child.handleClarifyConfirm}
        onClarifyBack={child.handleClarifyBack}
        onScopeSelect={child.handleScopeSelect}
        onDraftChange={child.handleDraftChange}
        onDraftSend={child.handleDraftSend}
        onSafetyChoice={child.handleSafetyChoice}
      />
    )
  }

  if (identity === 'parent') {
    return (
      <ChatShell
        identity="parent"
        messages={parent.messages}
        quickActions={parent.quickActions}
        inputPlaceholder="问问 AI 怎么跟孩子沟通…"
        onSendText={parent.handleUserText}
        onSwitchIdentity={handleSwitchIdentity}
        onParentReplySend={parent.handleReplySend}
      />
    )
  }

  // teacher
  return (
    <ChatShell
      identity="teacher"
      messages={teacher.messages}
      quickActions={teacher.quickActions}
      inputPlaceholder="记录你观察到的学生情况…"
      onSendText={teacher.handleUserText}
      onSwitchIdentity={handleSwitchIdentity}
    />
  )
}
