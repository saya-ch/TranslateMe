import { useMemo, useState } from 'react'
import type {
  ChildClarify,
  ChildStep,
  Identity,
  InboxMessage,
  ParentGuide,
  ParentMessageDraft,
  ParentStep,
  SafetyChoice,
  ShareScope,
  TeacherGuide,
  TeacherStep,
} from './types'
import { needsSafetyCheck } from './lib/safety'
import { buildClarifyDraft, buildParentMessageDraft, isActuallySent } from './lib/childBuilder'
import { buildParentGuide } from './lib/parentBuilder'
import { buildTeacherGuide } from './lib/teacherBuilder'
import { childSendMessageToParent, parentSendReplyToChild } from './lib/messageStore'
import { IdentitySelect } from './components/IdentitySelect'
import { SafetyPage, SafetyUnsafePage } from './components/SafetyPage'
import { ChildInput } from './components/ChildInput'
import { ChildClarifyPanel } from './components/ChildClarifyPanel'
import { ShareScopeSelect } from './components/ShareScopeSelect'
import { DraftPreview } from './components/DraftPreview'
import { ChildInbox } from './components/ChildInbox'
import { ParentInbox } from './components/ParentInbox'
import { ParentMessageView } from './components/ParentMessageView'
import { ParentAsk } from './components/ParentAsk'
import { ParentGuidePanel } from './components/ParentGuidePanel'
import { TeacherInput } from './components/TeacherInput'
import { TeacherGuidePanel } from './components/TeacherGuidePanel'
import { Footer } from './components/Footer'

type Phase = 'home' | 'identity' | 'child' | 'parent' | 'teacher' | 'safety-unsafe'

export default function App() {
  const [phase, setPhase] = useState<Phase>('home')
  const [identity, setIdentity] = useState<Identity | null>(null)

  // 孩子端状态
  const [childStep, setChildStep] = useState<ChildStep>('input')
  const [rawInput, setRawInput] = useState('')
  const [clarify, setClarify] = useState<ChildClarify | null>(null)
  const [scope, setScope] = useState<ShareScope | null>(null)
  const [draft, setDraft] = useState<ParentMessageDraft | null>(null)

  // 家长端状态
  const [parentStep, setParentStep] = useState<ParentStep>('inbox')
  const [openedMessage, setOpenedMessage] = useState<InboxMessage | null>(null)
  const [parentGuide, setParentGuide] = useState<ParentGuide | null>(null)

  // 老师端状态
  const [teacherStep, setTeacherStep] = useState<TeacherStep>('input')
  const [teacherGuide, setTeacherGuide] = useState<TeacherGuide | null>(null)

  const handleIdentity = (v: Identity) => {
    setIdentity(v)
    if (v === 'student') {
      setChildStep('input')
      setPhase('child')
    } else if (v === 'parent') {
      setParentStep('inbox')
      setPhase('parent')
    } else {
      setTeacherStep('input')
      setPhase('teacher')
    }
  }

  // ===== 孩子端流程 =====
  const handleChildSubmit = (text: string) => {
    setRawInput(text)
    if (needsSafetyCheck(text)) {
      setChildStep('safety')
    } else {
      setClarify(buildClarifyDraft(text))
      setChildStep('clarify')
    }
  }

  const handleSafetyChoice = (choice: SafetyChoice) => {
    if (choice === 'safe') {
      setClarify(buildClarifyDraft(rawInput))
      setChildStep('clarify')
    } else {
      setPhase('safety-unsafe')
    }
  }

  const handleClarifyConfirm = (c: ChildClarify) => {
    setClarify(c)
    setChildStep('scope')
  }

  const handleScopeChange = (s: ShareScope) => {
    setScope(s)
    if (clarify) {
      setDraft(buildParentMessageDraft(clarify, s))
    }
    setChildStep('preview')
  }

  const handleDraftConfirm = (edited: ParentMessageDraft) => {
    setDraft(edited)
    if (scope && isActuallySent(scope) && edited) {
      childSendMessageToParent({
        title: edited.title,
        body: edited.body,
        isVague: edited.isVague,
      })
    }
    setChildStep('sent')
  }

  // ===== 家长端流程 =====
  const handleParentAsk = (question: string) => {
    setParentGuide(buildParentGuide(question))
    setParentStep('guide')
  }

  const handleParentReply = (replyBody: string) => {
    parentSendReplyToChild({
      title: '家长通过帮我说出口发来一条回应',
      body: replyBody,
      isVague: false,
    })
    setParentStep('replied')
  }

  // ===== 老师端流程 =====
  const handleTeacherSubmit = (observation: string) => {
    setTeacherGuide(buildTeacherGuide(observation))
    setTeacherStep('guide')
  }

  // ===== 重置 =====
  const handleReset = () => {
    setPhase('home')
    setIdentity(null)
    setChildStep('input')
    setRawInput('')
    setClarify(null)
    setScope(null)
    setDraft(null)
    setParentStep('inbox')
    setOpenedMessage(null)
    setParentGuide(null)
    setTeacherStep('input')
    setTeacherGuide(null)
  }

  const headerTitle = useMemo(() => {
    if (phase === 'home') return '帮我说出口'
    if (phase === 'identity') return '你是谁？'
    if (phase === 'safety-unsafe') return '请先看这里'
    if (phase === 'child') {
      const map: Record<ChildStep, string> = {
        input: '说一句你现在最想说的',
        safety: '让我们先确认一下',
        clarify: '帮你整理想说的',
        scope: '你想怎么处理这段话？',
        preview: '预览草稿',
        sent: '已处理',
        inbox: '你的收件箱',
      }
      return map[childStep]
    }
    if (phase === 'parent') {
      const map: Record<ParentStep, string> = {
        inbox: '家长收件箱',
        message: '孩子发来的沟通请求',
        ask: '问问 AI 怎么回应',
        guide: 'AI 给你的建议',
        reply: '预览回应草稿',
        replied: '已发送',
      }
      return map[parentStep]
    }
    if (phase === 'teacher') {
      const map: Record<TeacherStep, string> = {
        input: '记录你观察到的情况',
        guide: '谈话建议',
        action: '下一步行动',
      }
      return map[teacherStep]
    }
    return '帮我说出口'
  }, [phase, childStep, parentStep, teacherStep])

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="app-header">
          <h1 className="app-title">{headerTitle}</h1>
          {phase === 'home' && (
            <p className="app-subtitle">
              一个围绕你建立的私密沟通中枢。AI 可以分别听见你、家长、老师的想法，但不会自动泄露任何一方原话。
            </p>
          )}
        </header>

        <main className="app-main">
          {phase === 'home' && (
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
          )}

          {phase === 'identity' && (
            <IdentitySelect value={identity} onChange={handleIdentity} />
          )}

          {phase === 'safety-unsafe' && <SafetyUnsafePage onReset={handleReset} />}

          {/* ===== 孩子端 ===== */}
          {phase === 'child' && childStep === 'input' && (
            <ChildInput onSubmit={handleChildSubmit} />
          )}

          {phase === 'child' && childStep === 'safety' && (
            <SafetyPage onChoose={handleSafetyChoice} />
          )}

          {phase === 'child' && childStep === 'clarify' && clarify && (
            <ChildClarifyPanel
              initial={clarify}
              onConfirm={handleClarifyConfirm}
              onBack={() => setChildStep('input')}
            />
          )}

          {phase === 'child' && childStep === 'scope' && (
            <ShareScopeSelect
              value={scope}
              onChange={handleScopeChange}
              onBack={() => setChildStep('clarify')}
            />
          )}

          {phase === 'child' && childStep === 'preview' && draft && scope && (
            <DraftPreview
              draft={draft}
              scope={scope}
              onConfirm={handleDraftConfirm}
              onBack={() => setChildStep('scope')}
            />
          )}

          {phase === 'child' && childStep === 'sent' && (
            <div className="sent-panel">
              <h3 className="sent-title">
                {scope && isActuallySent(scope) ? '已发送到家长端' : '草稿已保存'}
              </h3>
              <p className="panel-hint">
                {scope && isActuallySent(scope)
                  ? '家长会看到你确认后的内容，看不到你的原始输入和未分享的部分。'
                  : '这份草稿只有你自己能看到。你可以稍后自己决定怎么发。'}
              </p>
              <button
                type="button"
                className="primary-btn"
                onClick={() => setChildStep('inbox')}
              >
                查看我的收件箱
              </button>
              <button type="button" className="ghost-btn" onClick={handleReset}>
                返回首页
              </button>
            </div>
          )}

          {phase === 'child' && childStep === 'inbox' && (
            <ChildInbox onReset={handleReset} />
          )}

          {/* ===== 家长端 ===== */}
          {phase === 'parent' && parentStep === 'inbox' && (
            <ParentInbox
              onOpenMessage={(m) => {
                setOpenedMessage(m)
                setParentStep('message')
              }}
              onAskAI={() => setParentStep('ask')}
              onReset={handleReset}
            />
          )}

          {phase === 'parent' && parentStep === 'message' && openedMessage && (
            <ParentMessageView
              message={openedMessage}
              onAskAI={() => setParentStep('ask')}
              onBack={() => setParentStep('inbox')}
            />
          )}

          {phase === 'parent' && parentStep === 'ask' && (
            <ParentAsk
              onAsk={handleParentAsk}
              onBack={() => setParentStep('inbox')}
            />
          )}

          {phase === 'parent' && parentStep === 'guide' && parentGuide && (
            <ParentGuidePanel
              guide={parentGuide}
              onConfirmReply={handleParentReply}
              onBack={() => setParentStep('inbox')}
            />
          )}

          {phase === 'parent' && parentStep === 'replied' && (
            <div className="sent-panel">
              <h3 className="sent-title">回应已发送给孩子</h3>
              <p className="panel-hint">
                孩子会在 ta 的收件箱看到你的回应。记住，先听不评价，比说什么都重要。
              </p>
              <button type="button" className="ghost-btn" onClick={handleReset}>
                返回首页
              </button>
            </div>
          )}

          {/* ===== 老师端 ===== */}
          {phase === 'teacher' && teacherStep === 'input' && (
            <TeacherInput onSubmit={handleTeacherSubmit} />
          )}

          {phase === 'teacher' && teacherStep === 'guide' && teacherGuide && (
            <TeacherGuidePanel guide={teacherGuide} onReset={handleReset} />
          )}
        </main>

        <Footer />
      </div>
    </div>
  )
}
