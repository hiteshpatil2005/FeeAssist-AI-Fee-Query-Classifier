import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { GraduationCap, Sparkles, RefreshCw, Zap, Calendar, Receipt, CreditCard } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import ChatWindow from '../components/ChatWindow.jsx'
import LanguageSelector from '../components/LanguageSelector.jsx'
import { useAuth } from '../context/AuthContext'

const HEADER_ACTIONS = [
  { id: 'dues', label: 'Dues Snapshot', icon: Zap, query: 'How much fee is remaining for Semester 5?' },
  { id: 'dates', label: 'Due Deadlines', icon: Calendar, query: 'When is the last date to pay fees?' },
  { id: 'receipts', label: 'Fee Receipts', icon: Receipt, query: 'Show my previous fee payment receipts' },
  { id: 'installments', label: 'Installment Split', icon: CreditCard, query: 'Can I pay my fees in installments?' },
]

export default function Chat() {
  const { user } = useAuth()
  const location = useLocation()
  const [language, setLanguage] = useState(() => {
    if (user?.preferred_language === 'Hindi') return 'hi'
    if (user?.preferred_language === 'Marathi') return 'mr'
    return 'en'
  })

  useEffect(() => {
    if (user?.preferred_language) {
      if (user.preferred_language === 'Hindi') setLanguage('hi')
      else if (user.preferred_language === 'Marathi') setLanguage('mr')
      else setLanguage('en')
    }
  }, [user])

  const initialQuery = location.state?.initialQuery
  const [headerTrigger, setHeaderTrigger] = useState(null)
  const [sessionKey, setSessionKey] = useState(1)

  const handleResetSession = () => {
    setSessionKey((prev) => prev + 1)
  }

  return (
    <div className="flex flex-col md:flex-row h-screen bg-[#FAF8FF] overflow-hidden select-none">
      <Sidebar />

      {/* ── Main Dynamic Chat Area ────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Dynamic Glowing Background Blob */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl pointer-events-none -z-10" />
        <div className="absolute bottom-10 left-1/3 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl pointer-events-none -z-10" />

        {/* ── Enhanced Dynamic Header ────────────────────────────────────── */}
        <header className="px-4 py-3 bg-white/90 backdrop-blur-md border-b border-purple-100 shadow-2xs shrink-0 z-20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] flex items-center justify-center shrink-0 shadow-md shadow-purple-500/25">
                  <GraduationCap size={18} className="text-white" />
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 border border-white" />
                </span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold text-gray-900 leading-tight">FeeAssist AI</h2>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-[10px] font-bold text-emerald-700 border border-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Live Portal
                  </span>
                </div>
                <p className="text-[11px] text-gray-500 leading-tight mt-0.5">
                  {user?.name ? `Personal Assistant for ${user.name}` : 'Fee & Installment Assistant'}
                </p>
              </div>
            </div>

            {/* Mobile Reset */}
            <div className="flex items-center gap-1.5 sm:hidden">
              <button
                type="button"
                onClick={handleResetSession}
                title="Restart chat session"
                className="p-1.5 rounded-xl text-gray-500 hover:text-purple-700 hover:bg-purple-50 border border-purple-100"
              >
                <RefreshCw size={15} />
              </button>
            </div>
          </div>

          {/* Interactive Header Action Pills (Zero Emojis, Clean Professional Icons) */}
          <div className="hidden lg:flex items-center gap-1.5">
            {HEADER_ACTIONS.map((action) => {
              const ActionIcon = action.icon
              return (
                <button
                  key={action.id}
                  type="button"
                  onClick={() => setHeaderTrigger({ text: action.query, id: Date.now() })}
                  className="
                    px-2.5 py-1 rounded-xl text-[11px] font-semibold
                    bg-purple-50 hover:bg-purple-600 hover:text-white
                    text-purple-700 border border-purple-200/70
                    shadow-2xs hover:shadow-xs hover:scale-105 active:scale-95
                    transition-all duration-150 cursor-pointer flex items-center gap-1.5
                  "
                >
                  <ActionIcon size={12} />
                  <span>{action.label}</span>
                </button>
              )
            })}
          </div>

          {/* Right controls: Single Language Selector + New Chat Button (Single Voice button is in Chat Dock) */}
          <div className="flex items-center gap-2 self-end sm:self-auto">
            <LanguageSelector value={language} onChange={setLanguage} />
            <button
              type="button"
              onClick={handleResetSession}
              title="Start a new chat session"
              className="
                flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                text-gray-600 hover:text-purple-700 hover:bg-purple-50
                border border-purple-200/80 transition-all duration-150 cursor-pointer shadow-2xs hover:scale-105 active:scale-95
              "
            >
              <RefreshCw size={13} />
              <span>New Session</span>
            </button>
          </div>
        </header>

        {/* ── Chat Window (messages + interactive input) ────────────────── */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow
            key={sessionKey}
            language={language}
            initialQuery={initialQuery}
            headerTrigger={headerTrigger}
          />
        </div>
      </div>
    </div>
  )
}


