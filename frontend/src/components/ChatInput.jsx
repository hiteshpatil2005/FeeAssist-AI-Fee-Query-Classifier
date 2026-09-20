import { useRef, useState } from 'react'
import { Send, Mic } from 'lucide-react'

/**
 * ChatInput — Text input bar with send and microphone buttons.
 *
 * @param {object}   props
 * @param {function} props.onSend      - Callback with the trimmed message string
 * @param {boolean}  [props.disabled]  - Disable the input while waiting for response
 */
export default function ChatInput({ onSend, disabled = false }) {
  const [value, setValue] = useState('')
  const inputRef = useRef(null)

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    if (onSend) onSend(trimmed)
    setValue('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    // Send on Enter (without Shift for multiline)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = value.trim().length > 0 && !disabled

  return (
    <div className="
      flex items-center gap-2 p-3
      bg-white border-t border-[#E5E7EB]
    ">
      {/* Microphone (placeholder) */}
      <button
        id="chat-mic-button"
        type="button"
        title="Voice input (coming soon)"
        disabled
        className="
          flex-shrink-0 flex items-center justify-center
          w-10 h-10 rounded-lg
          border border-[#E5E7EB] text-[#9CA3AF]
          cursor-not-allowed
          transition-colors duration-150
        "
      >
        <Mic size={18} />
      </button>

      {/* Text Input */}
      <div className="flex-1 relative">
        <textarea
          id="chat-input"
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your fees..."
          disabled={disabled}
          rows={1}
          className="
            w-full resize-none px-4 py-2.5 pr-3
            text-sm text-[#1F2937] placeholder-[#9CA3AF]
            bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg
            focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
            disabled:opacity-60 disabled:cursor-not-allowed
            transition-colors duration-150
            leading-relaxed
            overflow-hidden
          "
          style={{ minHeight: '42px', maxHeight: '120px' }}
          onInput={(e) => {
            // Auto-resize textarea up to max height
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
          }}
        />
      </div>

      {/* Send Button */}
      <button
        id="chat-send-button"
        type="button"
        onClick={handleSend}
        disabled={!canSend}
        title="Send message"
        className="
          flex-shrink-0 flex items-center justify-center
          w-10 h-10 rounded-lg
          bg-[#6D28D9] text-white
          hover:bg-[#5b21b6]
          disabled:opacity-40 disabled:cursor-not-allowed
          transition-colors duration-150
          shadow-soft-sm
        "
      >
        <Send size={17} />
      </button>
    </div>
  )
}
