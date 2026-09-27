import { useState, useRef, useEffect, useCallback } from 'react'
import { Mic, MicOff, Loader2, Check, AlertCircle, X, Send } from 'lucide-react'

/**
 * VoiceButton — Single-Click Dynamic Voice Input (Speech-to-Text)
 * Professional, reliable, zero-latency speech recognition.
 *
 * Supported Languages:
 * - English ('en-IN')
 * - Hindi ('hi-IN')
 * - Marathi ('mr-IN')
 */
const BCP47_LANG_MAP = {
  en: 'en-IN',
  hi: 'hi-IN',
  mr: 'mr-IN',
}

const LANG_TITLES = {
  en: 'English',
  hi: 'Hindi',
  mr: 'Marathi',
}

export default function VoiceButton({
  language = 'en',
  onTranscript,
  onError,
  onStatusChange,
  className = '',
}) {
  const [status, setStatus] = useState('idle') // 'idle' | 'listening' | 'processing' | 'success' | 'error'
  const [feedback, setFeedback] = useState('')
  const recognitionRef = useRef(null)
  const isListeningRef = useRef(false)
  const transcriptBufferRef = useRef('')
  const resetTimerRef = useRef(null)

  // Safe state updater that keeps ref and state synchronized
  const setVoiceState = useCallback((newStatus, newFeedback = '') => {
    isListeningRef.current = (newStatus === 'listening')
    setStatus(newStatus)
    setFeedback(newFeedback)
    if (onStatusChange) {
      onStatusChange({ status: newStatus, feedback: newFeedback })
    }
  }, [onStatusChange])

  // Stop & cleanup recognition instance cleanly
  const cleanupRecognition = useCallback(() => {
    if (resetTimerRef.current) {
      clearTimeout(resetTimerRef.current)
      resetTimerRef.current = null
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onstart = null
        recognitionRef.current.onresult = null
        recognitionRef.current.onerror = null
        recognitionRef.current.onend = null
        recognitionRef.current.abort()
      } catch {
        // ignore abort errors
      }
      recognitionRef.current = null
    }
    isListeningRef.current = false
  }, [])

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      cleanupRecognition()
    }
  }, [cleanupRecognition])

  const stopAndSubmit = useCallback(() => {
    cleanupRecognition()
    const captured = transcriptBufferRef.current.trim()
    if (captured) {
      setVoiceState('success', captured)
      if (onTranscript) {
        onTranscript(captured)
      }
      resetTimerRef.current = setTimeout(() => {
        setVoiceState('idle', '')
      }, 1000)
    } else {
      setVoiceState('idle', '')
    }
  }, [cleanupRecognition, onTranscript, setVoiceState])

  const startListening = useCallback(() => {
    // 1. Immediately abort any existing recognition to avoid conflicts
    cleanupRecognition()
    transcriptBufferRef.current = ''

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      const err = 'Speech recognition is not supported in this browser. Please use Chrome or Edge.'
      setVoiceState('error', err)
      if (onError) onError(err)
      resetTimerRef.current = setTimeout(() => {
        setVoiceState('idle', '')
      }, 3000)
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognitionRef.current = recognition

      const bcp47 = BCP47_LANG_MAP[language] || 'en-IN'
      recognition.lang = bcp47
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        const prompt =
          language === 'mr'
            ? 'ऐकत आहे... बोला...'
            : language === 'hi'
            ? 'सुन रहा हूँ... बोलिए...'
            : 'Listening... speak now'
        setVoiceState('listening', prompt)
      }

      recognition.onresult = (event) => {
        let interim = ''
        let final = ''

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i]
          if (item.isFinal) {
            final += item[0].transcript + ' '
          } else {
            interim += item[0].transcript
          }
        }

        const combined = (final || interim || '').trim()
        if (combined) {
          transcriptBufferRef.current = combined
          setVoiceState('listening', combined)
        }
      }

      recognition.onerror = (event) => {
        let msg = ''
        if (event.error === 'not-allowed') {
          msg = 'Microphone permission denied. Please allow microphone in browser.'
        } else if (event.error === 'no-speech') {
          msg = 'No speech detected.'
        } else if (event.error === 'network') {
          msg = 'Network connection issue with speech service.'
        } else {
          msg = `Voice recognition notice (${event.error}).`
        }

        cleanupRecognition()
        setVoiceState('error', msg)
        if (onError) onError(msg)

        resetTimerRef.current = setTimeout(() => {
          setVoiceState('idle', '')
        }, 3000)
      }

      recognition.onend = () => {
        // If ended naturally while listening, submit buffered text or reset to idle
        if (isListeningRef.current) {
          stopAndSubmit()
        }
      }

      recognition.start()
      setVoiceState('listening', 'Initializing microphone...')
    } catch (err) {
      console.error('Recognition start error:', err)
      cleanupRecognition()
      setVoiceState('error', 'Microphone error.')
      resetTimerRef.current = setTimeout(() => {
        setVoiceState('idle', '')
      }, 3000)
    }
  }, [cleanupRecognition, language, onError, setVoiceState, stopAndSubmit])

  // Single Click Handler: Always toggle cleanly with 1 single click
  const handleClick = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (isListeningRef.current) {
      // If currently listening, 1 click immediately stops and submits
      stopAndSubmit()
    } else {
      // If idle, error, success, or anything else, 1 click immediately starts
      startListening()
    }
  }

  const isListening = status === 'listening'

  return (
    <div className="relative inline-flex items-center">
      {/* Listening Radar Waves */}
      {isListening && (
        <span className="absolute inset-0 rounded-2xl bg-purple-500 opacity-50 animate-ping pointer-events-none" />
      )}

      <button
        id="chat-voice-button"
        type="button"
        onClick={handleClick}
        title={
          isListening
            ? 'Click once to finish and send voice inquiry'
            : status === 'processing'
            ? 'Processing voice...'
            : `Voice inquiry (${LANG_TITLES[language] || 'English'}) - Click once to speak`
        }
        className={`
          relative flex items-center justify-center
          w-11 h-11 rounded-2xl
          transition-all duration-200 cursor-pointer shadow-xs active:scale-95
          ${
            isListening
              ? 'bg-gradient-to-tr from-purple-700 to-indigo-600 text-white shadow-lg shadow-purple-600/40 ring-4 ring-purple-200'
              : status === 'processing'
              ? 'bg-purple-100 text-purple-700 border border-purple-300 ring-2 ring-purple-200 animate-pulse'
              : status === 'success'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30'
              : status === 'error'
              ? 'bg-amber-100 text-amber-900 border border-amber-300'
              : 'bg-white hover:bg-purple-50 text-purple-700 hover:text-purple-900 border border-purple-200 hover:border-purple-300 hover:shadow-[0_0_12px_rgba(109,40,217,0.15)]'
          }
          ${className}
        `}
      >
        {isListening ? (
          <div className="flex items-center justify-center">
            <Mic size={18} className="animate-bounce text-white" />
          </div>
        ) : status === 'processing' ? (
          <Loader2 size={18} className="animate-spin text-purple-700" />
        ) : status === 'success' ? (
          <Check size={18} className="text-white" />
        ) : status === 'error' ? (
          <MicOff size={18} className="text-amber-800" />
        ) : (
          <div className="relative group-hover:scale-110 transition-transform">
            <Mic size={18} className="text-[#6D28D9]" />
          </div>
        )}
      </button>

      {/* Floating Status & Audio Waveform Popover for errors or quick notifications */}
      {status === 'error' && feedback && (
        <div
          role="status"
          aria-live="polite"
          className="
            absolute bottom-full mb-3 left-1/2 -translate-x-1/2 z-50
            px-3.5 py-1.5 rounded-xl text-xs font-semibold shadow-xl backdrop-blur-md
            pointer-events-none transition-all duration-300 flex items-center gap-2 min-w-[180px] justify-center
            bg-gray-900/95 text-white ring-2 ring-purple-300/40 animate-fade-in-up
          "
        >
          <AlertCircle size={13} className="text-amber-300 shrink-0" />
          <span className="truncate max-w-xs">{feedback}</span>
        </div>
      )}
    </div>
  )
}

