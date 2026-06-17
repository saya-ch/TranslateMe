import type { SafetyChoice } from '../../../types'

interface SafetyChatCardProps {
  id: string
  choice: SafetyChoice
  onChoose: (id: string, choice: 'safe' | 'unsafe') => void
}

export function SafetyChatCard({ id, choice, onChoose }: SafetyChatCardProps) {
  return (
    <div className="chat-card safety-chat-card">
      <div className="card-header">
        <span className="card-ai-tag safety-tag">AI</span>
        <span className="card-title safety-title">让我们先确认一下</span>
      </div>

      <p className="safety-card-text">
        这句话让我们想先确认一下你现在的状态。它可能只是一时的情绪化表达，也可能你真的现在很难受。两种情况都正常，我们都想先确认一下。
      </p>

      <div className="safety-resource">
        <div className="safety-resource-title">心理支持与求助咨询</div>
        <ul className="safety-resource-list">
          <li><strong>12355</strong> 青少年服务热线</li>
          <li><strong>12356</strong> 心理援助热线</li>
          <li>身边可信成年人、紧急联系人、学校心理老师</li>
        </ul>
      </div>

      <div className="safety-resource danger">
        <div className="safety-resource-title">如存在立即人身危险</div>
        <ul className="safety-resource-list">
          <li>请拨打 <strong>110</strong>（报警）/ <strong>120</strong>（急救）</li>
        </ul>
      </div>

      <p className="safety-card-note">
        这个工具不能替代专业人员，也不会询问危险方式、地点、计划等细节。
      </p>

      <div className="safety-choose">
        <p className="safety-choose-title">你现在的情况是？</p>
        {choice === null && (
          <>
            <button
              type="button"
              className="card-primary-btn"
              onClick={() => onChoose(id, 'safe')}
            >
              我现在安全，只是想整理表达
            </button>
            <button
              type="button"
              className="card-danger-btn"
              onClick={() => onChoose(id, 'unsafe')}
            >
              我不太安全 / 我身边马上有危险
            </button>
          </>
        )}
        {choice === 'safe' && (
          <div className="card-done-tag">你选择了：继续整理表达</div>
        )}
        {choice === 'unsafe' && (
          <div className="card-done-tag danger-tag">你选择了：先联系真人帮助</div>
        )}
      </div>
    </div>
  )
}
