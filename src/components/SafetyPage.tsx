interface SafetyPageProps {
  onReset: () => void
}

export function SafetyPage({ onReset }: SafetyPageProps) {
  return (
    <div className="safety-page">
      <div className="safety-card">
        <h2 className="safety-title">这可能需要立即的真人帮助</h2>

        <p className="safety-text">
          如果你或身边的人正处于立即危险中，请立刻联系身边可信成年人、紧急联系人或学校心理老师。
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
