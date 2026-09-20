import { Mic } from 'lucide-react'

/**
 * VoiceButton — Microphone icon button.
 *
 * This is a UI placeholder only.
 * Voice (speech-to-text) functionality will be implemented in a future phase.
 *
 * @param {object} props
 * @param {boolean}  props.compact  - If true, renders a smaller version (for ChatInput)
 * @param {string}   props.className - Additional Tailwind classes
 */
export default function VoiceButton({ compact = false, className = '' }) {
  const handleClick = () => {
    // TODO: Implement Web Speech API voice input
    console.info('Voice input is not yet implemented.')
  }

  if (compact) {
    return (
      <button
        id="voice-button"
        type="button"
        onClick={handleClick}
        title="Voice input (coming soon)"
        className={`
          flex items-center justify-center
          w-10 h-10 rounded-lg
          text-[#6B7280] hover:text-[#6D28D9] hover:bg-[#F3E8FF]
          border border-[#E5E7EB] hover:border-[#8B5CF6]
          transition-colors duration-150
          disabled:opacity-50 disabled:cursor-not-allowed
          ${className}
        `}
        disabled
      >
        <Mic size={18} />
      </button>
    )
  }

  return (
    <button
      id="voice-button-header"
      type="button"
      onClick={handleClick}
      title="Voice input (coming soon)"
      className={`
        flex items-center justify-center gap-2
        px-3 py-2 rounded-lg text-sm font-medium
        text-[#6B7280] hover:text-[#6D28D9] hover:bg-[#F3E8FF]
        border border-[#E5E7EB] hover:border-[#8B5CF6]
        transition-colors duration-150
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      disabled
    >
      <Mic size={16} />
      <span>Voice</span>
    </button>
  )
}
