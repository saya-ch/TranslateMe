import type { ActionCards } from '../types'
import { cardToText } from '../lib/generator'
import { CopyButton } from './CopyButton'

interface ActionCardsProps {
  cards: ActionCards
  onReset: () => void
}

export function ActionCards({ cards, onReset }: ActionCardsProps) {
  return (
    <div className="cards-wrap">
      {cards.sources.length > 0 && (
        <div className="sources-row">
          <span className="sources-label">识别到的压力来源：</span>
          {cards.sources.map((s) => (
            <span key={s.key} className="source-tag">{s.label}</span>
          ))}
        </div>
      )}

      {/* 给自己的卡 */}
      <section className="action-card card-self">
        <header className="card-head">
          <h3>给自己的卡</h3>
          <CopyButton text={cardToText(cards, 'self')} />
        </header>
        <div className="card-body">
          <p className="card-block">
            <span className="block-label">可能你想说的是</span>
            {cards.self.restate}
          </p>
          <p className="card-block">
            <span className="block-label">一句可以直接发出去的话</span>
            {cards.self.sendable}
          </p>
          <p className="card-block">
            <span className="block-label">一个很小的下一步</span>
            {cards.self.nextStep}
          </p>
        </div>
      </section>

      {/* 给家长的卡 */}
      <section className="action-card card-parent">
        <header className="card-head">
          <h3>给家长的卡</h3>
          <CopyButton text={cardToText(cards, 'parent')} />
        </header>
        <div className="card-body">
          <p className="card-block">
            <span className="block-label">孩子这句话可能在表达</span>
            {cards.parent.understand}
          </p>
          <div className="card-block">
            <span className="block-label">可以说的三句话</span>
            <ol className="card-list">
              {cards.parent.sayThree.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ol>
          </div>
          <div className="card-block">
            <span className="block-label">暂时不要说的三句话</span>
            <ol className="card-list not-list">
              {cards.parent.notSayThree.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ol>
          </div>
          <p className="card-block">
            <span className="block-label">下一步建议</span>
            {cards.parent.nextStep}
          </p>
        </div>
      </section>

      {/* 给老师的卡 */}
      <section className="action-card card-teacher">
        <header className="card-head">
          <h3>给老师的卡</h3>
          <CopyButton text={cardToText(cards, 'teacher')} />
        </header>
        <div className="card-body">
          <p className="card-block">
            <span className="block-label">情况摘要</span>
            {cards.teacher.summary}
          </p>
          <div className="card-block">
            <span className="block-label">第一次谈话建议</span>
            <ol className="card-list">
              {cards.teacher.talkAdvice.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ol>
          </div>
          <div className="card-block">
            <span className="block-label">观察点</span>
            <ul className="card-list">
              {cards.teacher.observePoints.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <p className="card-block refer-block">
            <span className="block-label">转介建议</span>
            {cards.teacher.referAdvice}
          </p>
        </div>
      </section>

      <button type="button" className="ghost-btn" onClick={onReset}>
        重新输入
      </button>
    </div>
  )
}
