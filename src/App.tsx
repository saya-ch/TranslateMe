import { useMemo, useState } from 'react'
import type { ActionCards as ActionCardsData, Identity, Scene, Step } from './types'
import { isHighRisk } from './lib/safety'
import { generateCards } from './lib/generator'
import { IdentitySelect } from './components/IdentitySelect'
import { SceneSelect } from './components/SceneSelect'
import { InputPanel } from './components/InputPanel'
import { ActionCards } from './components/ActionCards'
import { SafetyPage } from './components/SafetyPage'
import { Footer } from './components/Footer'

export default function App() {
  const [step, setStep] = useState<Step>('home')
  const [identity, setIdentity] = useState<Identity | null>(null)
  const [scene, setScene] = useState<Scene | null>(null)
  const [input, setInput] = useState('')
  const [cards, setCards] = useState<ActionCardsData | null>(null)

  const handleIdentity = (v: Identity) => {
    setIdentity(v)
    setStep('scene')
  }

  const handleScene = (v: Scene) => {
    setScene(v)
    if (v === 'urgent') {
      // 情况比较紧急：直接进安全支持页，无需输入
      setStep('safety')
      return
    }
    setStep('input')
  }

  const handleSubmit = () => {
    const text = input.trim()
    if (!text) return
    // 高风险拦截：先检测，命中即跳安全页，不生成卡片
    if (isHighRisk(text)) {
      setStep('safety')
      return
    }
    const result = generateCards(text, identity ?? 'student', scene ?? 'sort-out')
    setCards(result)
    setStep('result')
  }

  const handleReset = () => {
    setStep('home')
    setIdentity(null)
    setScene(null)
    setInput('')
    setCards(null)
  }

  const headerTitle = useMemo(() => {
    switch (step) {
      case 'home':
        return '帮我说出口'
      case 'identity':
        return '你是谁？'
      case 'scene':
        return '你想做什么？'
      case 'input':
        return '说一句你现在最想说的'
      case 'result':
        return '这是帮你整理的三张卡'
      case 'safety':
        return '请先看这里'
      default:
        return '帮我说出口'
    }
  }, [step])

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="app-header">
          <h1 className="app-title">{headerTitle}</h1>
          {step === 'home' && (
            <p className="app-subtitle">
              把说不出口的一句话，变成能给自己、家长、老师看的三张行动卡。
            </p>
          )}
        </header>

        <main className="app-main">
          {step === 'home' && (
            <div className="home-block">
              <p className="home-intro">
                很多时候不是不想求助，而是不知道怎么开口。
                <br />
                在这里写下一句话，我们帮你把它整理成可以发出去、可以行动的内容。
              </p>
              <div className="home-safe-note">
                如果你现在情况比较紧急，可以直接选择「情况比较紧急」查看真人帮助渠道。
              </div>
              <button
                type="button"
                className="primary-btn"
                onClick={() => setStep('identity')}
              >
                开始
              </button>
            </div>
          )}

          {step === 'identity' && (
            <IdentitySelect value={identity} onChange={handleIdentity} />
          )}

          {step === 'scene' && (
            <SceneSelect value={scene} onChange={handleScene} />
          )}

          {step === 'input' && (
            <InputPanel
              value={input}
              onChange={setInput}
              onSubmit={handleSubmit}
            />
          )}

          {step === 'result' && cards && (
            <ActionCards cards={cards} onReset={handleReset} />
          )}

          {step === 'safety' && <SafetyPage onReset={handleReset} />}
        </main>

        <Footer />
      </div>
    </div>
  )
}
