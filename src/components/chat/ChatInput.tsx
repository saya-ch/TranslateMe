import { useState } from 'react'

interface ChatInputProps {
  onSend: (text: string) => void
  placeholder?: string
}

export function ChatInput({ onSend, placeholder }: ChatInputProps) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed) return
    onSend(trimmed)
    setValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-input-bar">
      <textarea
        className="chat-input"
        placeholder={placeholder || '说一句你现在最想说的…'}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        maxLength={200}
      />
      <button
        type="button"
        className="chat-send-btn"
        onClick={handleSend}
        disabled={!value.trim()}
        aria-label="发送"
      >
        发送
      </button>
    </div>
  )
}
