import { useRef, useState } from 'react'
import { Send, Sparkles, Mic, Volume2, X, Radio } from 'lucide-react'
import VoiceButton from './VoiceButton.jsx'

/**
 * ChatInput — Dynamic, interactive floating input dock with animated voice spectrum and quick prompt chips.
 */
const QUICK_CHIPS = [
  { label: 'Pending Balance', text: 'How much fee is remaining for Semester 5?' },
  { label: 'Due Date', text: 'When is the last date to pay fees?' },
  { label: 'हिंदी: फीस तपशील', text: 'मेरी कुल कितनी फीस बाकी है?' },
  { label: 'मराठी: हप्ते सुविधा', text: 'मी 2 हप्त्यांमध्ये फी भरू शकतो का?' },
  { label: 'Fee Receipts', text: 'Show my previous fee payment receipts' },
  { label: 'Scholarship Status', text: 'What scholarship or concession is applied?' },
]

export default function ChatInput({ onSend, disabled = false, language = 'en' }) {
  const [value, setValue] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [voiceState, setVoiceState] = useState({ status: 'idle', feedback: '' })
  const inputRef = useRef(null)

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    if (onSend) onSend(trimmed)
    setValue('')
    if (inputRef.current) {
      inputRef.current.style.height = '40px'
      inputRef.current.focus()
    }
  }

  const handleVoiceTranscript = (transcript) => {
    if (!transcript || disabled) return
    if (onSend) {
      onSend(transcript)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleChipClick = (chipText) => {
    if (disabled) return
    if (onSend) onSend(chipText)
  }

  const handleClear = () => {
    setValue('')
    if (inputRef.current) {
      inputRef.current.style.height = '40px'
      inputRef.current.focus()
    }
  }

  const canSend = value.trim().length > 0 && !disabled

  const getLangBadge = () => {
    if (language === 'hi') return 'Hindi Audio'
    if (language === 'mr') return 'Marathi Audio'
    return 'English Audio'
  }

  const isListening = voiceState.status === 'listening'

  return (
    <div className="p-3 sm:p-4 bg-gradient-to-t from-[#FAF8FF] via-white/80 to-transparent">
      {/* ── Interactive Quick Prompt Chips Bar (Zero Emojis) ──────────────── */}
      <div className="max-w-4xl mx-auto mb-2 flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1">
        <span className="text-[10px] uppercase font-bold text-purple-700 flex-shrink-0 flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-purple-100/70">
          <Sparkles size={11} className="text-purple-600" />
          Quick Inquiries:
        </span>
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip.label}
            type="button"
            onClick={() => handleChipClick(chip.text)}
            disabled={disabled}
            className="
              px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap
              bg-white/95 hover:bg-purple-600 hover:text-white
              text-gray-700 border border-purple-200/90
              shadow-2xs hover:shadow-xs hover:scale-105 active:scale-95
              transition-all duration-150 cursor-pointer flex-shrink-0
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* ── Dynamic Floating Elevated Input Dock ──────────────────────────── */}
      <div
        className={`
          max-w-4xl mx-auto rounded-3xl bg-white/95 backdrop-blur-md
          border transition-all duration-300 shadow-[0_8px_32px_rgba(109,40,217,0.08)] p-2 sm:p-2.5
          ${
            isListening
              ? 'border-purple-600 ring-4 ring-purple-100 shadow-[0_12px_36px_rgba(109,40,217,0.2)]'
              : isFocused
              ? 'border-purple-500 shadow-[0_12px_36px_rgba(109,40,217,0.18)] ring-4 ring-purple-100'
              : 'border-purple-200/90 hover:border-purple-300'
          }
        `}
      >
        {/* Dynamic Voice Active Sound Wave Banner (Non-destructive overlay) */}
        {isListening && (
          <div className="mb-2 px-3.5 py-2 bg-gradient-to-r from-purple-50 via-indigo-50 to-purple-50 rounded-2xl border border-purple-200/80 flex items-center justify-between animate-fade-in-up">
            <div className="flex items-center gap-3">
              {/* 8-bar Dynamic Audio Spectrum Visualizer */}
              <div className="flex items-end gap-[3px] h-5 px-1">
                <span className="w-1 bg-gradient-to-t from-purple-700 to-indigo-500 rounded-full animate-spec-1" />
                <span className="w-1 bg-gradient-to-t from-purple-700 to-indigo-500 rounded-full animate-spec-2" />
                <span className="w-1 bg-gradient-to-t from-indigo-600 to-purple-400 rounded-full animate-spec-3" />
                <span className="w-1 bg-gradient-to-t from-indigo-600 to-purple-400 rounded-full animate-spec-4" />
                <span className="w-1 bg-gradient-to-t from-purple-600 to-indigo-400 rounded-full animate-spec-5" />
                <span className="w-1 bg-gradient-to-t from-purple-600 to-indigo-400 rounded-full animate-spec-6" />
                <span className="w-1 bg-gradient-to-t from-purple-700 to-indigo-500 rounded-full animate-spec-7" />
                <span className="w-1 bg-gradient-to-t from-purple-700 to-indigo-500 rounded-full animate-spec-8" />
              </div>

              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-purple-800 animate-pulse flex items-center gap-1">
                    <Radio size={12} className="text-purple-600" />
                    Listening Now
                  </span>
                  <span className="text-[10px] font-semibold px-2 py-0.2 rounded-full bg-purple-100 text-purple-800">
                    {language === 'mr' ? 'Marathi' : language === 'hi' ? 'Hindi' : 'English'}
                  </span>
                </div>
                <p className="text-xs text-purple-900 font-medium truncate max-w-xs sm:max-w-md mt-0.5">
                  {voiceState.feedback || 'Speak your fee question now...'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-purple-700">
              <span className="animate-pulse">Click mic to finish</span>
            </div>
          </div>
        )}

        <div className="flex items-end gap-2">
          {/* The Single Persistent Dynamic Voice Button — NEVER unmounted */}
          <div className="flex-shrink-0 pb-0.5">
            <VoiceButton
              language={language}
              onTranscript={handleVoiceTranscript}
              onStatusChange={setVoiceState}
            />
          </div>

          {/* Text Area */}
          <div className="flex-1 relative pb-1">
            <textarea
              id="chat-input"
              ref={inputRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={
                isListening
                  ? 'Listening to speech... (or type your question)'
                  : 'Ask anything about your fees, installments, due dates, or receipts...'
              }
              disabled={disabled}
              rows={1}
              className="
                w-full resize-none px-2 py-1.5
                text-sm text-gray-900 placeholder-gray-400
                bg-transparent focus:outline-none
                disabled:opacity-60 disabled:cursor-not-allowed
                leading-relaxed overflow-hidden transition-all
              "
              style={{ minHeight: '40px', maxHeight: '120px' }}
              onInput={(e) => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
              }}
            />
          </div>

          {/* Clear button if text typed */}
          {value.length > 0 && !disabled && (
            <div className="pb-2.5 flex-shrink-0">
              <button
                type="button"
                onClick={handleClear}
                title="Clear text"
                className="p-1 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          )}

          {/* Language Status Pill & Animated Send Button */}
          <div className="flex items-center gap-2 pb-0.5 flex-shrink-0">
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-purple-50 text-[10px] font-semibold text-purple-700 border border-purple-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              {getLangBadge()}
            </span>

            <button
              id="chat-send-button"
              type="button"
              onClick={handleSend}
              disabled={!canSend}
              title="Send message (Enter)"
              className={`
                flex items-center justify-center
                w-11 h-11 rounded-2xl transition-all duration-200 cursor-pointer
                ${
                  canSend
                    ? 'bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-md shadow-purple-500/30 hover:scale-105 active:scale-95 hover:shadow-lg'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              <Send size={18} className={canSend ? 'translate-x-0.5 -translate-y-0.5' : ''} />
            </button>
          </div>
        </div>
      </div>

    </div>
  )
}

