import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import ChatWindow from '../components/ChatWindow.jsx'
import LanguageSelector from '../components/LanguageSelector.jsx'
import VoiceButton from '../components/VoiceButton.jsx'
import { useAuth } from '../context/AuthContext'

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

  return (
    <div className="flex flex-col md:flex-row h-screen bg-white overflow-hidden">
      <Sidebar />

      {/* ── Main Chat Area ────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Chat Header */}
        <header className="flex items-center justify-between px-5 py-4 bg-white border-b border-[#E5E7EB] shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-[#6D28D9] flex items-center justify-center shrink-0 shadow-soft-sm">
              <GraduationCap size={16} className="text-white" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-[#1F2937] leading-tight">FeeAssist AI</h2>
              <p className="text-xs text-[#6B7280] leading-tight">
                {user?.name ? `Assisting ${user.name}` : 'Personal Fees Assistant'}
              </p>
            </div>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            <LanguageSelector value={language} onChange={setLanguage} />
            <VoiceButton />
          </div>
        </header>

        {/* Chat Window (messages + input) */}
        <div className="flex-1 overflow-hidden bg-[#FAFAFA]">
          <ChatWindow language={language} initialQuery={initialQuery} />
        </div>
      </div>
    </div>
  )
}
