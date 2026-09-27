import { useState, useEffect, useRef } from 'react'
import {
  GraduationCap,
  Send,
  Mic,
  Sparkles,
  CheckCheck,
  Volume2,
  Play,
  Pause,
  RotateCcw,
} from 'lucide-react'

// Simulated conversation script for auto-showcase
const SCRIPT = [
  {
    id: 1,
    role: 'user',
    text: 'What is my pending fee for Semester 5?',
    lang: 'EN',
    badge: 'English',
  },
  {
    id: 2,
    role: 'assistant',
    text: 'Your outstanding balance is ₹25,000.00 due by 15 Nov 2026.',
    lang: 'EN',
    badge: 'Verified DB',
    intent: 'PENDING_FEE',
  },
  {
    id: 3,
    role: 'user',
    text: 'मेरी कुल कितनी फीस बाकी है?',
    lang: 'HI',
    badge: 'हिंदी',
  },
  {
    id: 4,
    role: 'assistant',
    text: 'सेमेस्टर 5 के लिए आपकी बकाया फीस ₹25,000.00 है।',
    lang: 'HI',
    badge: 'हिंदी उत्तर',
    intent: 'PENDING_FEE',
  },
  {
    id: 5,
    role: 'user',
    text: 'मी 2 हप्त्यांमध्ये भरू शकतो का?',
    lang: 'MR',
    badge: 'मराठी',
  },
  {
    id: 6,
    role: 'assistant',
    text: 'हो, तुम्ही ₹12,500.00 चे 2 समान हप्ते करू शकता.',
    lang: 'MR',
    badge: 'मराठी उत्तर',
    intent: 'INSTALLMENT',
  },
  {
    id: 7,
    role: 'user',
    text: 'When is the last date to pay fees?',
    lang: 'EN',
    badge: 'English',
  },
  {
    id: 8,
    role: 'assistant',
    text: 'The official fee due date is 15 November 2026.',
    lang: 'EN',
    badge: 'Verified DB',
    intent: 'DUE_DATE',
  },
]

// Quick prompt suggestions
const QUICK_PROMPTS = [
  { label: 'Pending Fee?', text: 'What is my pending fee for Semester 5?', lang: 'EN' },
  { label: 'हिंदी: बकाया फीस?', text: 'मेरी कुल कितनी फीस बाकी है?', lang: 'HI' },
  { label: 'मराठी: हप्ते?', text: 'मी 2 हप्त्यांमध्ये भरू शकतो का?', lang: 'MR' },
  { label: 'Due Date?', text: 'When is the last date to pay fees?', lang: 'EN' },
]

export default function LiveChatShowcase() {
  const [messages, setMessages] = useState([SCRIPT[0], SCRIPT[1], SCRIPT[2]])
  const [currentIndex, setCurrentIndex] = useState(3)
  const [isTyping, setIsTyping] = useState(false)
  const [inputText, setInputText] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [isAutoPlaying, setIsAutoPlaying] = useState(true)
  const [isSpeakingId, setIsSpeakingId] = useState(null)
  const chatScrollRef = useRef(null)
  const autoPlayTimerRef = useRef(null)

  // Smooth scroll to bottom on every message or typing state change
  const scrollToBottom = () => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: 'smooth',
      })
    }
  }

  useEffect(() => {
    const timer = setTimeout(scrollToBottom, 60)
    return () => clearTimeout(timer)
  }, [messages, isTyping])

  // Automatic demo progression
  useEffect(() => {
    if (!isAutoPlaying) return

    const nextItem = SCRIPT[currentIndex]
    let timeoutId

    if (nextItem.role === 'user') {
      // Simulate user typing smoothly in the input bar
      let charIdx = 0
      const fullText = nextItem.text
      setInputText('')

      const typeInterval = setInterval(() => {
        charIdx++
        setInputText(fullText.slice(0, charIdx))
        if (charIdx >= fullText.length) {
          clearInterval(typeInterval)
          setIsSending(true)
          timeoutId = setTimeout(() => {
            setIsSending(false)
            setInputText('')
            setMessages((prev) => [...prev, nextItem].slice(-5))
            setCurrentIndex((idx) => (idx + 1) % SCRIPT.length)
          }, 450)
        }
      }, 35)

      return () => {
        clearInterval(typeInterval)
        clearTimeout(timeoutId)
      }
    } else {
      // Assistant replying: display typing indicator smoothly
      setIsTyping(true)
      timeoutId = setTimeout(() => {
        setIsTyping(false)
        setMessages((prev) => [...prev, nextItem].slice(-5))
        setCurrentIndex((idx) => (idx + 1) % SCRIPT.length)
      }, 1200)

      return () => clearTimeout(timeoutId)
    }
  }, [currentIndex, isAutoPlaying])

  // Interactive handler: Send custom message from input or chip
  const handleSendMessage = (customText) => {
    const textToSend = (customText || inputText).trim()
    if (!textToSend) return

    // Pause autoplay so user can explore
    setIsAutoPlaying(false)
    setInputText('')
    setIsSending(true)

    // Detect language
    const hasDevanagari = /[\u0900-\u097F]/.test(textToSend)
    const isMarathi = hasDevanagari && /(माझी|किती|आहे|हप्ते|करा|तारीख|हो)/.test(textToSend)
    const lang = isMarathi ? 'MR' : hasDevanagari ? 'HI' : 'EN'
    const badge = isMarathi ? 'मराठी' : hasDevanagari ? 'हिंदी' : 'English'

    const newUserMsg = {
      id: Date.now(),
      role: 'user',
      text: textToSend,
      lang,
      badge,
    }

    setMessages((prev) => [...prev, newUserMsg].slice(-5))
    setIsSending(false)

    // Trigger AI response after short typing delay
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      let reply = 'Your remaining fee is ₹25,000.00 for Semester 5 due on 15 Nov 2026.'
      let replyBadge = 'Verified DB'

      if (lang === 'HI') {
        reply = 'सेमेस्टर 5 के लिए आपकी बकाया फीस ₹25,000.00 है, जिसकी देय तिथि 15 नवंबर 2026 है।'
        replyBadge = 'हिंदी उत्तर'
      } else if (lang === 'MR') {
        reply = 'सेमिस्टर 5 साठी तुमची शिल्लक फी ₹25,000.00 आहे. देय तारीख 15 नोव्हेंबर 2026 आहे.'
        replyBadge = 'मराठी उत्तर'
      } else if (/receipt|download/i.test(textToSend)) {
        reply = 'Official fee payment receipt #REC-2025-08-20 for ₹50,000.00 is generated.'
      } else if (/installment|split|emi/i.test(textToSend)) {
        reply = 'You can pay the remaining ₹25,000 in 2 monthly installments of ₹12,500 each.'
      }

      const newAssistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        text: reply,
        lang,
        badge: replyBadge,
      }

      setMessages((prev) => [...prev, newAssistantMsg].slice(-5))
    }, 900)
  }

  // Interactive TTS audio playback
  const handlePlaySpeech = (msg) => {
    if (!window.speechSynthesis) return

    if (isSpeakingId === msg.id) {
      window.speechSynthesis.cancel()
      setIsSpeakingId(null)
      return
    }

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(msg.text.replace(/₹/g, ' Rupees '))
    if (msg.lang === 'HI') utterance.lang = 'hi-IN'
    else if (msg.lang === 'MR') utterance.lang = 'mr-IN'
    else utterance.lang = 'en-IN'

    utterance.onend = () => setIsSpeakingId(null)
    utterance.onerror = () => setIsSpeakingId(null)

    setIsSpeakingId(msg.id)
    window.speechSynthesis.speak(utterance)
  }

  return (
    <div className="relative w-full max-w-lg lg:max-w-xl rounded-3xl bg-white/95 backdrop-blur-xl border border-purple-200/90 shadow-[0_20px_50px_rgba(109,40,217,0.15)] overflow-hidden transition-all duration-300 hover:shadow-[0_24px_60px_rgba(109,40,217,0.22)]">
      {/* ── Top Header Bar ──────────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-[#6D28D9] via-[#7C3AED] to-[#8B5CF6] px-5 py-3.5 text-white flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center border border-white/30 shadow-inner">
              <GraduationCap size={18} className="text-white" />
            </div>
            {/* Pulsing online green dot */}
            <span className="absolute -bottom-0.5 -right-0.5 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400 border-2 border-[#6D28D9]" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold tracking-wide">FeeAssist AI Live Experience</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/20 font-semibold text-purple-100 uppercase tracking-wider">
                Interactive
              </span>
            </div>
            <p className="text-[11px] text-purple-200 font-normal">
              Try asking in English, हिंदी, or मराठी
            </p>
          </div>
        </div>

        {/* Right Controls: Auto-demo Play/Pause + Sound Wave */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsAutoPlaying((v) => !v)}
            title={isAutoPlaying ? 'Pause auto-demo' : 'Resume auto-demo'}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/15 hover:bg-white/25 border border-white/20 text-xs text-white transition-all active:scale-95"
          >
            {isAutoPlaying ? <Pause size={12} /> : <Play size={12} />}
            <span className="text-[11px] font-medium hidden sm:inline">
              {isAutoPlaying ? 'Pause' : 'Auto Play'}
            </span>
          </button>

          {/* Sound Wave Bars */}
          <div className="flex items-center gap-1.5 bg-white/10 px-2 py-1.5 rounded-full border border-white/15">
            <Volume2 size={13} className="text-purple-200" />
            <div className="flex items-end gap-[2px] h-3.5 w-4">
              <span className={`w-[2.5px] bg-white rounded-full ${isAutoPlaying ? 'animate-wave-1' : 'h-1'}`} />
              <span className={`w-[2.5px] bg-white rounded-full ${isAutoPlaying ? 'animate-wave-2' : 'h-2'}`} />
              <span className={`w-[2.5px] bg-white rounded-full ${isAutoPlaying ? 'animate-wave-3' : 'h-1.5'}`} />
              <span className={`w-[2.5px] bg-white rounded-full ${isAutoPlaying ? 'animate-wave-4' : 'h-2.5'}`} />
            </div>
          </div>
        </div>
      </div>

      {/* ── Interactive Quick Chips ────────────────────────────────────── */}
      <div className="px-4 py-2 bg-purple-50/80 border-b border-purple-100/80 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
        <span className="text-[10px] uppercase font-bold text-purple-600 flex-shrink-0 flex items-center gap-1">
          <Sparkles size={11} />
          Try:
        </span>
        {QUICK_PROMPTS.map((q) => (
          <button
            key={q.label}
            type="button"
            onClick={() => handleSendMessage(q.text)}
            className="px-2.5 py-1 rounded-full bg-white hover:bg-purple-600 hover:text-white border border-purple-200 text-[11px] font-medium text-purple-900 transition-all shadow-2xs hover:scale-105 active:scale-95 flex-shrink-0"
          >
            {q.label}
          </button>
        ))}
      </div>

      {/* ── Message Stream Viewport (Generous 340px height) ───────────── */}
      <div
        ref={chatScrollRef}
        className="p-4 space-y-3.5 h-[340px] overflow-y-auto smooth-scroll flex flex-col bg-gradient-to-b from-[#FAF5FF]/60 via-white to-[#FBF8FF]"
      >
        {messages.map((m) => {
          const isUser = m.role === 'user'
          return (
            <div
              key={m.id}
              className={`flex items-start gap-2.5 animate-message-in ${
                isUser ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0 text-[11px] font-bold shadow-xs ${
                  isUser
                    ? 'bg-[#EDE9FE] text-[#6D28D9] border border-purple-200'
                    : 'bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-purple-500/20'
                }`}
              >
                {isUser ? 'You' : <GraduationCap size={14} />}
              </div>

              {/* Bubble Content */}
              <div
                className={`max-w-[84%] px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed transition-all shadow-xs ${
                  isUser
                    ? 'bg-[#6D28D9] text-white rounded-tr-xs'
                    : 'bg-white border border-purple-100 text-[#1F2937] rounded-tl-xs shadow-[0_4px_12px_rgba(0,0,0,0.04)] hover:border-purple-200'
                }`}
              >
                {/* Header Tag / Audio Controls */}
                <div
                  className={`flex items-center justify-between gap-2 mb-1.5 text-[10px] font-semibold ${
                    isUser ? 'text-purple-200 justify-end' : 'text-purple-600'
                  }`}
                >
                  <span className="flex items-center gap-1">
                    {m.badge}
                    {isUser && <CheckCheck size={12} className="text-purple-200" />}
                  </span>

                  {!isUser && (
                    <button
                      type="button"
                      onClick={() => handlePlaySpeech(m)}
                      title="Listen to response"
                      className="text-purple-500 hover:text-purple-800 p-0.5 rounded transition-colors"
                    >
                      <Volume2 size={12} className={isSpeakingId === m.id ? 'text-emerald-600 animate-pulse' : ''} />
                    </button>
                  )}
                </div>

                <p className="font-normal text-[12.5px] leading-snug">{m.text}</p>
              </div>
            </div>
          )
        })}

        {/* AI Typing Indicator */}
        {isTyping && (
          <div className="flex items-start gap-2.5 animate-message-in">
            <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] flex items-center justify-center text-white flex-shrink-0 shadow-xs">
              <GraduationCap size={14} />
            </div>
            <div className="bg-white border border-purple-100 rounded-2xl rounded-tl-xs px-3.5 py-2.5 text-xs shadow-xs flex items-center gap-2 text-gray-500">
              <span className="text-[11px] text-purple-600 font-semibold mr-1">FeeAssist AI is typing</span>
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}
      </div>

      {/* ── Interactive Input Form ────────────────────────────────────── */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSendMessage()
        }}
        className="px-4 py-3 bg-[#FAF7FF] border-t border-purple-100 flex items-center gap-2.5"
      >
        <div className="flex-1 bg-white border border-purple-200 rounded-2xl px-3.5 py-2 flex items-center justify-between text-xs shadow-inner focus-within:ring-2 focus-within:ring-purple-400 focus-within:border-purple-500 transition-all">
          <input
            type="text"
            value={inputText}
            onChange={(e) => {
              setIsAutoPlaying(false) // pause auto-demo when user types
              setInputText(e.target.value)
            }}
            placeholder="Type a fee question in English, हिंदी, मराठी..."
            className="w-full bg-transparent text-gray-800 placeholder-gray-400 text-xs focus:outline-none pr-2"
          />
          <button
            type="button"
            title="Speech input"
            onClick={() => handleSendMessage('What is my pending fee for Semester 5?')}
            className="text-purple-500 hover:text-purple-700 transition-colors p-1"
          >
            <Mic size={14} />
          </button>
        </div>

        <button
          type="submit"
          disabled={!inputText.trim() && !isSending}
          aria-label="Send query"
          className={`w-9 h-9 rounded-2xl flex items-center justify-center transition-all ${
            isSending || inputText.trim()
              ? 'bg-[#6D28D9] hover:bg-purple-700 text-white shadow-md shadow-purple-500/30 scale-105 active:scale-95'
              : 'bg-purple-200 text-purple-400 cursor-not-allowed'
          }`}
        >
          <Send size={14} className={isSending ? 'translate-x-0.5 -translate-y-0.5' : ''} />
        </button>
      </form>

      {/* ── Mini Footer Status ────────────────────────────────────────── */}
      <div className="px-4 py-1.5 bg-purple-50/70 border-t border-purple-100/60 flex items-center justify-between text-[11px] text-purple-800">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Interactive Demo • Voice & Multilingual Ready
        </span>
        <button
          type="button"
          onClick={() => {
            setMessages([SCRIPT[0], SCRIPT[1], SCRIPT[2]])
            setCurrentIndex(3)
            setIsAutoPlaying(true)
          }}
          className="flex items-center gap-1 text-[10px] text-purple-600 hover:text-purple-900 font-semibold hover:underline"
        >
          <RotateCcw size={10} />
          Restart Demo
        </button>
      </div>
    </div>
  )
}
