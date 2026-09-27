import { useState, useRef, useEffect } from 'react'
import { Bot, CheckCircle2, Volume2, Square } from 'lucide-react'
import { voiceService } from '../services/api'

/**
 * MessageBubble — Renders a single chat message with optional TTS audio playback.
 *
 * @param {object}  props
 * @param {'user'|'assistant'} props.role         - Who sent the message
 * @param {string}  props.content                 - Message text
 * @param {string}  [props.timestamp]             - Optional display timestamp string
 * @param {boolean} [props.isTyping]              - Show animated typing indicator instead of content
 * @param {string}  [props.intent]                - Detected NLP intent
 * @param {number}  [props.confidence]            - Intent classification confidence
 * @param {string}  [props.detectedLanguage]      - Language tag ('en', 'hi', 'mr')
 * @param {string}  [props.source]                - 'ml' | 'gemini' | 'guardrail'
 * @param {boolean} [props.fallbackUsed]          - If Gemini fallback was used
 * @param {Array}   [props.options]               - Interactive disambiguation options
 * @param {Function}[props.onOptionClick]         - Callback when an option chip is selected
 */
const LANG_LABELS = {
  mr: 'मराठी',
  hi: 'हिंदी',
  en: 'English',
}

export default function MessageBubble({
  role,
  content,
  timestamp,
  isTyping = false,
  intent,
  confidence,
  detectedLanguage,
  options,
  source,
  fallbackUsed,
  onOptionClick,
}) {
  const isUser = role === 'user'
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef(null)

  // Clean up audio playback on unmount
  useEffect(() => {
    return () => {
      stopAudio()
    }
  }, [])

  const stopAudio = () => {
    if (window.speechSynthesis) {
      try {
        window.speechSynthesis.cancel()
      } catch {
        // ignore
      }
    }
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    setIsPlaying(false)
  }

  const playAudio = () => {
    stopAudio()

    if (!content) return

    // Clean text for natural speech pronunciation
    let textToSpeak = content
      .replace(/(\*\*|__)(.*?)\1/g, '$2')
      .replace(/^[•\-\*]\s*/gm, '')
      .replace(/₹/g, detectedLanguage === 'en' ? ' Rupees ' : ' रुपये ')
      .replace(/\n+/g, '. ')
      .trim()

    if (!textToSpeak) return

    // Prefer browser SpeechSynthesis if supported
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel()
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume()
        }

        const utterance = new SpeechSynthesisUtterance(textToSpeak)
        const bcp47 =
          detectedLanguage === 'mr'
            ? 'mr-IN'
            : detectedLanguage === 'hi'
            ? 'hi-IN'
            : 'en-IN'
        utterance.lang = bcp47
        utterance.rate = 1.0

        utterance.onstart = () => setIsPlaying(true)
        utterance.onend = () => setIsPlaying(false)
        utterance.onerror = () => {
          setIsPlaying(false)
          fallbackToBackendTts(textToSpeak)
        }

        setIsPlaying(true)
        window.speechSynthesis.speak(utterance)
        return
      } catch {
        // Fallback to backend TTS stream
      }
    }

    fallbackToBackendTts(textToSpeak)
  }

  const fallbackToBackendTts = (text) => {
    try {
      const url = voiceService.getTtsUrl(text, detectedLanguage || 'en')
      const audio = new Audio(url)
      audioRef.current = audio
      audio.onended = () => setIsPlaying(false)
      audio.onerror = () => setIsPlaying(false)
      setIsPlaying(true)
      audio.play().catch(() => setIsPlaying(false))
    } catch {
      setIsPlaying(false)
    }
  }

  const toggleAudio = () => {
    if (isPlaying) {
      stopAudio()
    } else {
      playAudio()
    }
  }

  // Format markdown bold (**text**) safely into formatted JSX
  const formatText = (text) => {
    if (!text) return ''
    const parts = text.split(/(\*\*.*?\*\*)/g)
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        )
      }
      return part
    })
  }

  return (
    <div
      className={`
        flex items-end gap-2 animate-fade-in-up
        ${isUser ? 'flex-row-reverse' : 'flex-row'}
      `}
    >
      {/* Avatar (assistant only) */}
      {!isUser && (
        <div
          className="
          shrink-0 w-8 h-8 rounded-full
          bg-[#6D28D9] flex items-center justify-center
          shadow-soft-sm
        "
        >
          <Bot size={16} className="text-white" />
        </div>
      )}

      {/* Bubble */}
      <div
        className={`
          max-w-[85%] md:max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed
          shadow-soft-sm
          ${
            isUser
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
            {/* Intent & Language Badges for Assistant Messages (Zero Emojis) */}
            {!isUser && (intent || detectedLanguage) && (
              <div className="flex items-center justify-between gap-1.5 mb-2 pb-1.5 border-b border-slate-100 text-[11px] font-medium text-purple-700">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <CheckCircle2 size={12} className="text-purple-600" />
                  <span>
                    Intent:{' '}
                    <span className="font-semibold">{intent || 'FEE_QUERY'}</span>
                  </span>
                  {confidence !== undefined && confidence !== null && (
                    <span className="text-slate-400">
                      · {(confidence * 100).toFixed(0)}%
                    </span>
                  )}
                  {source === 'gemini' && (
                    <span className="ml-1 px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 text-[10px] font-semibold border border-amber-200">
                      Gemini Verified
                    </span>
                  )}
                  {source === 'guardrail' && (
                    <span className="ml-1 px-1.5 py-0.5 rounded bg-blue-50 text-blue-800 text-[10px] font-semibold border border-blue-200">
                      Guardrail Active
                    </span>
                  )}
                </div>
                {detectedLanguage && (
                  <span className="px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 text-[10px] font-semibold border border-purple-100">
                    {LANG_LABELS[detectedLanguage] || detectedLanguage.toUpperCase()}
                  </span>
                )}
              </div>
            )}


            <div className="m-0 whitespace-pre-wrap break-words">
              {formatText(content)}
            </div>

            {/* Interactive Options Chips (Disambiguation) */}
            {options && options.length > 0 && onOptionClick && (
              <div className="mt-3 pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">
                {options.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() =>
                      onOptionClick(
                        `Check Semester ${opt.semester} (${opt.academic_year})`
                      )
                    }
                    className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 transition-colors"
                  >
                    Semester {opt.semester} ({opt.academic_year})
                  </button>
                ))}
              </div>
            )}

            {/* Bottom bar with TTS Audio Controls & Timestamp */}
            <div className="mt-2 pt-1 flex items-center justify-between gap-2 border-t border-slate-50">
              {!isUser ? (
                <button
                  type="button"
                  onClick={toggleAudio}
                  title={isPlaying ? 'Stop listening' : 'Listen to message'}
                  className={`
                    inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium transition-colors cursor-pointer
                    ${
                      isPlaying
                        ? 'bg-purple-100 text-purple-800 border border-purple-300'
                        : 'text-slate-500 hover:text-purple-700 hover:bg-purple-50'
                    }
                  `}
                >
                  {isPlaying ? (
                    <>
                      <Square size={11} className="fill-purple-800" />
                      <span>Stop</span>
                      <span className="flex items-center gap-0.5 ml-0.5">
                        <span className="w-1 h-2 bg-purple-600 rounded-full animate-bounce" />
                        <span className="w-1 h-3 bg-purple-600 rounded-full animate-bounce [animation-delay:0.15s]" />
                        <span className="w-1 h-2 bg-purple-600 rounded-full animate-bounce [animation-delay:0.3s]" />
                      </span>
                    </>
                  ) : (
                    <>
                      <Volume2 size={12} />
                      <span>Listen</span>
                    </>
                  )}
                </button>
              ) : (
                <div />
              )}

              {timestamp && (
                <p
                  className={`
                    text-[10px] leading-none
                    ${isUser ? 'text-purple-200' : 'text-[#9CA3AF]'}
                  `}
                >
                  {timestamp}
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
