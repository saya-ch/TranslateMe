import type { SafetyChoice } from '../types'

interface SafetyPageProps {
  onChoose: (choice: SafetyChoice) => void
}

export function SafetyPage({ onChoose }: SafetyPageProps) {
  return (
    <div className="safety-page">
      <div className="safety-card">
        <h2 className="safety-title">让我们先确认一下</h2>

        <p className="safety-text">
          这句话让我们想先确认一下你现在的状态。
          <br />
          它可能只是一时的情绪化表达，也可能你真的现在很难受。两种情况都正常，我们都想先确认一下。
        </p>

        <p className="safety-note">
          如果你现在需要真人支持，可以随时联系下面这些渠道：
        </p>

        <div className="safety-section">
          <div className="safety-section-title">心理支持与求助咨询</div>
          <ul className="safety-list">
            <li>
              <strong>12355</strong> 青少年服务热线
            </li>
            <li>
              <strong>12356</strong> 心理援助热线
            </li>
            <li>身边可信成年人、紧急联系人、学校心理老师</li>
          </ul>
        </div>

        <div className="safety-section danger-section">
          <div className="safety-section-title">如存在立即人身危险</div>
          <ul className="safety-list">
            <li>
              请拨打 <strong>110</strong>（报警）/ <strong>120</strong>（急救）
            </li>
          </ul>
        </div>

        <p className="safety-note">
          这个工具不能替代专业人员，也不会询问危险方式、地点、计划等细节。
        </p>

        <div className="safety-choose">
          <p className="safety-choose-title">你现在的情况是？</p>
          <button
            type="button"
            className="primary-btn"
            onClick={() => onChoose('safe')}
          >
            我现在安全，只是想整理表达
          </button>
          <button
            type="button"
            className="ghost-btn danger-ghost"
            onClick={() => onChoose('unsafe')}
          >
            我不太安全 / 我身边马上有危险
          </button>
        </div>
      </div>
    </div>
  )
}

// 不安全分支：只显示支持资源，不进入普通整理流程
export function SafetyUnsafePage({ onReset }: { onReset: () => void }) {
  return (
    <div className="safety-page">
      <div className="safety-card">
        <h2 className="safety-title">请先联系真人帮助</h2>

        <p className="safety-text">
          谢谢你愿意告诉我们。你现在不需要继续整理表达，请先联系下面的人或渠道。
        </p>

        <div className="safety-section">
          <div className="safety-section-title">心理支持与求助咨询</div>
          <ul className="safety-list">
            <li>
              <strong>12355</strong> 青少年服务热线
            </li>
            <li>
              <strong>12356</strong> 心理援助热线
            </li>
            <li>身边可信成年人、紧急联系人、学校心理老师</li>
          </ul>
        </div>

        <div className="safety-section danger-section">
          <div className="safety-section-title">如存在立即人身危险</div>
          <ul className="safety-list">
            <li>
              请拨打 <strong>110</strong>（报警）/ <strong>120</strong>（急救）
            </li>
          </ul>
        </div>

        <p className="safety-note">
          这个工具不能替代专业人员，也不会继续分析危险细节。
        </p>

        <button type="button" className="ghost-btn" onClick={onReset}>
          返回首页
        </button>
      </div>
    </div>
  )
}
