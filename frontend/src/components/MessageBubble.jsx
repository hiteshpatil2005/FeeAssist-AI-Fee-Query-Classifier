import { Bot } from 'lucide-react'

/**
 * MessageBubble — Renders a single chat message.
 *
 * @param {object}  props
 * @param {'user'|'assistant'} props.role       - Who sent the message
 * @param {string}  props.content               - Message text
 * @param {string}  [props.timestamp]           - Optional display timestamp string
 * @param {boolean} [props.isTyping]            - Show animated typing indicator instead of content
 */
export default function MessageBubble({ role, content, timestamp, isTyping = false }) {
  const isUser = role === 'user'

  return (
    <div
      className={`
        flex items-end gap-2 animate-fade-in-up
        ${isUser ? 'flex-row-reverse' : 'flex-row'}
      `}
    >
      {/* Avatar (assistant only) */}
      {!isUser && (
        <div className="
          flex-shrink-0 w-8 h-8 rounded-full
          bg-[#6D28D9] flex items-center justify-center
          shadow-soft-sm
        ">
          <Bot size={16} className="text-white" />
        </div>
      )}

      {/* Bubble */}
      <div
        className={`
          max-w-[75%] md:max-w-[65%] px-4 py-3 rounded-2xl text-sm leading-relaxed
          shadow-soft-sm
          ${isUser
            ? 'bg-[#6D28D9] text-white rounded-br-sm'
            : 'bg-white text-[#1F2937] border border-[#E5E7EB] rounded-bl-sm'
          }
        `}
      >
        {isTyping ? (
          /* Typing indicator dots */
          <div className="flex items-center gap-1 py-1">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        ) : (
          <>
            <p className="m-0 whitespace-pre-wrap break-words">{content}</p>
            {timestamp && (
              <p className={`
                mt-1 text-[10px] text-right leading-none
                ${isUser ? 'text-purple-200' : 'text-[#9CA3AF]'}
              `}>
                {timestamp}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
