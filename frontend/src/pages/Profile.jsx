import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  User,
  Mail,
  BookOpen,
  Calendar,
  Globe,
  ShieldCheck,
  LogOut,
  Sparkles,
} from 'lucide-react'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [copied, setCopied] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleCopyId = () => {
    if (user?.id) {
      navigator.clipboard.writeText(String(user.id))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const initial = user?.name ? user.name.charAt(0).toUpperCase() : 'S'

  return (
    <div className="flex flex-col md:flex-row h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar />

      <main className="flex-1 flex flex-col h-full overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-5 sticky top-0 z-10">
          <h1 className="text-xl font-bold text-slate-800">Student Profile</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Your registered student identity and conversational preferences
          </p>
        </header>

        {/* Profile Card */}
        <div className="p-6 max-w-4xl w-full mx-auto space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-soft overflow-hidden">
            {/* Banner Header */}
            <div className="h-28 bg-linear-to-r from-purple-700 via-purple-600 to-indigo-700 p-6 flex items-end">
              <div className="translate-y-8 flex items-center gap-4">
                <div className="w-20 h-20 rounded-2xl bg-white p-1.5 shadow-md">
                  <div className="w-full h-full rounded-xl bg-purple-100 flex items-center justify-center text-2xl font-black text-purple-700">
                    {initial}
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-12 px-6 pb-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{user?.name || 'Student Name'}</h2>
                  <p className="text-xs text-slate-500 mt-0.5">{user?.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleCopyId}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-600 transition-colors shadow-xs"
                  >
                    {copied ? 'Copied Student ID!' : `Student ID: #${user?.id || '—'}`}
                  </button>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="px-3 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    <LogOut size={13} />
                    Sign out
                  </button>
                </div>
              </div>

              {/* Detail Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
                    <User size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Full Name</span>
                    <span className="text-sm font-semibold text-slate-800">{user?.name}</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
                    <Mail size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Email Address</span>
                    <span className="text-sm font-semibold text-slate-800">{user?.email}</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
                    <BookOpen size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Program / Course</span>
                    <span className="text-sm font-semibold text-slate-800">{user?.course || 'Computer Science'}</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
                    <Calendar size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Current Semester</span>
                    <span className="text-sm font-semibold text-slate-800">
                      {user?.semester ? `Semester ${user.semester}` : 'Semester 5'} {user?.year ? `(Year ${user.year})` : ''}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
                    <Globe size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Preferred Query Language</span>
                    <span className="text-sm font-semibold text-purple-700">
                      {user?.preferred_language || 'English'}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
                    <ShieldCheck size={18} />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Account Status</span>
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md mt-0.5">
                      Active & Verified
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Assistant integration card */}
          <div className="p-6 bg-purple-50 border border-purple-200 rounded-2xl flex items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles size={16} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-purple-900">Personalized Fee Answers</h3>
                <p className="text-xs text-purple-700 mt-0.5">
                  The AI assistant uses your student ID to query your specific semester fee records, scholarships, and payment history securely.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors shrink-0"
            >
              Go to Chat
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
