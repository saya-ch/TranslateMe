import { useState } from 'react'
import { TEACHER_EXAMPLES } from '../data/examples'

interface TeacherInputProps {
  onSubmit: (observation: string) => void
}

export function TeacherInput({ onSubmit }: TeacherInputProps) {
  const [value, setValue] = useState('')

  return (
    <div className="input-panel">
      <p className="panel-hint">
        在这里记录你观察到的情况。这些内容只有你自己能看到，不会自动告知家长或其他老师。
      </p>

      <textarea
        className="input-box"
        placeholder="比如：学生最近上课走神，作业也不交"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        rows={4}
        maxLength={200}
      />

      <div className="examples">
        <div className="examples-title">不知道怎么记？点一下试试：</div>
        <div className="examples-list">
          {TEACHER_EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              className="example-chip"
              onClick={() => setValue(ex.text)}
            >
              {ex.text}
            </button>
          ))}
        </div>
      </div>

      <button
        type="button"
        className="primary-btn"
        disabled={!value.trim()}
        onClick={() => onSubmit(value)}
      >
        帮我整理谈话建议
      </button>
    </div>
  )
}
