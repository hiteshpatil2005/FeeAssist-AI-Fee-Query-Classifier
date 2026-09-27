import { useEffect, useRef, useState } from 'react'
import { Sparkles, DollarSign, Calendar, CreditCard, Receipt, MessageCircle, ArrowRight } from 'lucide-react'
import MessageBubble from './MessageBubble.jsx'
import ChatInput from './ChatInput.jsx'
import { useAuth } from '../context/AuthContext'
import { chatService } from '../services/api'

function formatTime(date) {
  return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

let nextId = 100

const HERO_CARDS = [
  {
    icon: DollarSign,
    title: 'Pending Fee Balance',
    desc: 'Instant breakdown of tuition, lab, library & remaining dues',
    query: 'How much fee is remaining for Semester 5?',
    color: 'from-purple-500/10 to-indigo-500/10 text-purple-700 border-purple-200/80',
  },
  {
    icon: Calendar,
    title: 'Due Dates & Deadlines',
    desc: 'Never miss payment cutoffs and avoid late penalties',
    query: 'When is the last date to pay fees for Semester 5?',
    color: 'from-amber-500/10 to-orange-500/10 text-amber-700 border-amber-200/80',
  },
  {
    icon: CreditCard,
    title: 'Installment Split Options',
    desc: 'Check eligibility for paying semester fees in 2 or 3 parts',
    query: 'Can I pay my fees in installments?',
    color: 'from-emerald-500/10 to-teal-500/10 text-emerald-700 border-emerald-200/80',
  },
  {
    icon: Receipt,
    title: 'Payment Receipts',
    desc: 'Verify transaction IDs, download dates & paid amounts',
    query: 'Show my previous fee payment receipts',
    color: 'from-blue-500/10 to-cyan-500/10 text-blue-700 border-blue-200/80',
  },
]

export default function ChatWindow({ language, initialQuery, headerTrigger }) {
  const { user } = useAuth()
  const sessionIdRef = useRef(`sess_${user?.id || 'guest'}_${Date.now()}`)

  const [messages, setMessages] = useState(() => [
    {
      id: 1,
      role: 'assistant',
      content: `Hello${user?.name ? ' ' + user.name.split(' ')[0] : ''}! I am FeeAssist AI, your personal college fees assistant.\n\nI am connected to your official fee records. You can ask about your pending balance, fee structure, payment deadlines, scholarship deductions, installment schedules, or previous receipts in English, Hindi, or Marathi.`,
      timestamp: formatTime(new Date()),
    },
  ])
  const [waiting, setWaiting] = useState(false)
  const bottomRef = useRef(null)
  const initialQueryHandled = useRef(false)

  const SUGGESTED_QUESTIONS = [
    "How much fee is remaining?",
    "When is my fee due date?",
    "Can I pay in installments?",
    "Show my payment receipts",
    "मेरी फीस कितनी बाकी है?",
    "माझी किती फी बाकी आहे?",
  ]

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, waiting])

  const sendMessage = async (text) => {
    const trimmed = text.trim()
    if (!trimmed || waiting) return

    const userMsg = {
      id: nextId++,
      role: 'user',
      content: trimmed,
      timestamp: formatTime(new Date()),
    }
    setMessages((prev) => [...prev, userMsg])
    setWaiting(true)

    try {
      const response = await chatService.sendMessage({
        message: trimmed,
        session_id: sessionIdRef.current,
        language: language || 'en',
      })

      const data = response.data
      const assistantMsg = {
        id: nextId++,
        role: 'assistant',
        content: data.message,
        timestamp: formatTime(new Date()),
        intent: data.intent,
        confidence: data.confidence,
        detectedLanguage: data.detected_language,
        options: data.options,
        fallbackUsed: data.fallback_used,
        source: data.source,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error('Chat error:', err)
      const errorMsg = {
        id: nextId++,
        role: 'assistant',
        content:
          err.response?.data?.detail ||
          'Sorry, I encountered an issue connecting to the Fee Service. Please try again or check your connection.',
        timestamp: formatTime(new Date()),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setWaiting(false)
    }
  }

  // Handle incoming initialQuery from MyFees or navigation
  useEffect(() => {
    if (initialQuery && !initialQueryHandled.current) {
      initialQueryHandled.current = true
      sendMessage(initialQuery)
    }
  }, [initialQuery])

  // Handle header action pill triggers
  useEffect(() => {
    if (headerTrigger?.text) {
      sendMessage(headerTrigger.text)
    }
  }, [headerTrigger])


  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-transparent via-white/50 to-purple-50/20">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 smooth-scroll">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
            intent={msg.intent}
            confidence={msg.confidence}
            detectedLanguage={msg.detectedLanguage}
            options={msg.options}
            source={msg.source}
            fallbackUsed={msg.fallbackUsed}
            onOptionClick={sendMessage}
          />
        ))}

        {/* Typing indicator while waiting */}
        {waiting && <MessageBubble role="assistant" isTyping />}

        {/* Interactive Dynamic Hero Cards when chat just started */}
        {messages.length === 1 && !waiting && (
          <div className="py-2 space-y-4 animate-chat-slide-up">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {HERO_CARDS.map((card, idx) => {
                const Icon = card.icon
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => sendMessage(card.query)}
                    className={`
                      p-3.5 rounded-2xl bg-gradient-to-br ${card.color}
                      border shadow-2xs hover:shadow-md hover:scale-[1.02] active:scale-[0.98]
                      transition-all duration-200 text-left cursor-pointer flex flex-col justify-between group
                    `}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="w-8 h-8 rounded-xl bg-white/90 shadow-2xs flex items-center justify-center">
                          <Icon size={16} />
                        </div>
                        <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                      </div>
                      <h4 className="text-xs font-bold text-gray-900 mb-0.5">{card.title}</h4>
                      <p className="text-[11px] text-gray-500 leading-snug">{card.desc}</p>
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Suggested quick questions */}
            <div className="pt-1 max-w-2xl mx-auto">
              <p className="text-[11px] text-purple-700 font-bold uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Sparkles size={12} className="text-amber-500" />
                Frequently Asked Inquiries
              </p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => sendMessage(q)}
                    className="
                      px-3 py-1.5 text-xs rounded-xl cursor-pointer font-medium
                      bg-white/95 border border-purple-200/80 text-gray-700
                      hover:border-purple-600 hover:text-purple-700 hover:bg-purple-50/80 hover:scale-105 active:scale-95
                      transition-all duration-150 text-left shadow-2xs
                    "
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Dynamic Elevated Chat Input Bar */}
      <ChatInput onSend={sendMessage} disabled={waiting} language={language} />
    </div>
  )
}

