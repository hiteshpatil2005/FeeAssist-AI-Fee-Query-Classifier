import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  MessageSquare,
  Receipt,
  Clock,
  User,
  LogOut,
  GraduationCap,
  Menu,
  X,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Volume2,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { feeService } from '../services/api'

const NAV_ITEMS = [
  { id: 'chat',            label: 'Chat Assistant',  icon: MessageSquare, path: '/chat',     badge: 'AI v2' },
  { id: 'my-fees',         label: 'My Fees',         icon: Receipt,       path: '/fees',     badge: null },
  { id: 'payment-history', label: 'Payment History', icon: Clock,         path: '/payments', badge: null },
  { id: 'profile',         label: 'Student Profile', icon: User,          path: '/profile',  badge: null },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [feeSummary, setFeeSummary] = useState(null)

  useEffect(() => {
    // Quick peek of student's fee summary
    feeService
      .getSummary()
      .then((res) => setFeeSummary(res.data))
      .catch(() => {})
  }, [location.pathname])

  const handleNav = (path) => {
    navigate(path)
    setMobileOpen(false)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userName = user?.name || 'Student'
  const userEmail = user?.email || 'student@college.edu'
  const initial = userName.charAt(0).toUpperCase()
  const preferredLang = user?.preferred_language || 'English'

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-gradient-to-b from-[#FDFBFF] via-[#FAF7FF] to-[#F5F0FF] select-none">
      {/* ── Brand Header ────────────────────────────────────────────── */}
      <div className="px-5 py-4 border-b border-purple-100/80 bg-white/70 backdrop-blur-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative group cursor-pointer" onClick={() => handleNav('/chat')}>
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] flex items-center justify-center shadow-md shadow-purple-500/25 group-hover:scale-105 transition-transform duration-200">
              <GraduationCap size={19} className="text-white" />
            </div>
            {/* Pulsing online beacon */}
            <span className="absolute -bottom-0.5 -right-0.5 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400 border border-white" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <p className="text-sm font-bold text-gray-900 leading-tight">FeeAssist AI</p>
              <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-purple-100 text-purple-800 font-semibold uppercase tracking-wider">
                Active
              </span>
            </div>
            <p className="text-[11px] text-purple-600 font-medium leading-tight mt-0.5">
              Multilingual Assistant
            </p>
          </div>
        </div>
      </div>

      {/* ── Navigation List ──────────────────────────────────────────── */}
      <div className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        <p className="px-3 text-[10px] uppercase font-bold tracking-wider text-gray-400 mb-2">
          Navigation
        </p>

        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const active = location.pathname === item.path

          return (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              type="button"
              onClick={() => handleNav(item.path)}
              className={`
                group relative w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl
                text-xs font-semibold text-left transition-all duration-200 cursor-pointer
                ${
                  active
                    ? 'bg-white text-purple-900 shadow-[0_4px_16px_rgba(109,40,217,0.1)] border border-purple-200/90 translate-x-1'
                    : 'text-gray-600 hover:bg-white/80 hover:text-purple-700 hover:translate-x-1 border border-transparent'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`
                    w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200
                    ${
                      active
                        ? 'bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-sm'
                        : 'bg-purple-50 text-purple-600 group-hover:bg-purple-100'
                    }
                  `}
                >
                  <Icon size={15} />
                </div>
                <span>{item.label}</span>
              </div>

              {/* Dynamic badge or indicator */}
              {item.badge ? (
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-2xs">
                  {item.badge}
                </span>
              ) : active ? (
                <div className="w-1.5 h-1.5 rounded-full bg-purple-600 animate-pulse" />
              ) : null}
            </button>
          )
        })}

        {/* ── Quick Fees Snapshot Glance Card ────────────────────────── */}
        <div className="pt-4 px-1">
          <div className="p-3.5 rounded-2xl bg-gradient-to-br from-white via-purple-50/50 to-indigo-50/40 border border-purple-200/70 shadow-2xs hover:shadow-xs transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 flex items-center gap-1">
                <Zap size={11} className="text-amber-500 fill-amber-500" />
                Fee Glance
              </span>
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md bg-purple-100 text-purple-800">
                {feeSummary ? `Sem ${feeSummary.semester || 5}` : 'Dues'}
              </span>
            </div>

            <div className="space-y-1 mb-2.5">
              <p className="text-[11px] text-gray-500 font-medium">Pending Balance</p>
              <p className="text-base font-extrabold text-gray-900 tracking-tight">
                {feeSummary
                  ? `₹${Number(feeSummary.pending_amount).toLocaleString('en-IN')}`
                  : '₹25,000.00'}
              </p>
            </div>

            <button
              type="button"
              onClick={() => handleNav('/fees')}
              className="w-full py-1.5 px-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-all shadow-xs hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>View Breakdown</span>
              <ArrowRight size={12} />
            </button>
          </div>
        </div>

        {/* ── Voice & Engine Status Card ─────────────────────────────── */}
        <div className="pt-2 px-1">
          <div className="p-3 rounded-2xl bg-purple-100/50 border border-purple-200/60 flex items-center justify-between text-xs text-purple-900">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-purple-600 text-white flex items-center justify-center flex-shrink-0">
                <Volume2 size={13} />
              </div>
              <div>
                <p className="text-[11px] font-bold leading-tight">Voice AI Ready</p>
                <p className="text-[9px] text-purple-600 leading-tight">EN • HI • MR Support</p>
              </div>
            </div>
            {/* Animated sound equalizer */}
            <div className="flex items-end gap-[2px] h-3 w-3.5">
              <span className="w-[2px] bg-purple-600 rounded-full animate-wave-1" />
              <span className="w-[2px] bg-purple-600 rounded-full animate-wave-2" />
              <span className="w-[2px] bg-purple-600 rounded-full animate-wave-3" />
            </div>
          </div>
        </div>
      </div>

      {/* ── User Footer Card ─────────────────────────────────────────── */}
      <div className="p-3 border-t border-purple-100/80 bg-white/80 backdrop-blur-xs">
        <div className="p-2.5 rounded-2xl bg-purple-50/60 border border-purple-100/70 mb-2.5 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white flex items-center justify-center text-xs font-bold shadow-xs flex-shrink-0">
            {initial}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-gray-900 truncate leading-tight">{userName}</p>
            <p className="text-[10px] text-purple-700 truncate leading-tight font-medium mt-0.5">
              Lang: {preferredLang}
            </p>
          </div>
        </div>

        <button
          id="logout-button"
          type="button"
          onClick={handleLogout}
          className="
            w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-xl
            text-xs font-semibold text-gray-600 hover:text-red-700 hover:bg-red-50
            border border-transparent hover:border-red-200 transition-all duration-150
          "
        >
          <LogOut size={13} />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* ── Desktop Sidebar ─────────────────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-64 flex-shrink-0 border-r border-purple-100/90 h-screen sticky top-0 shadow-sm z-30">
        <SidebarContent />
      </aside>

      {/* ── Mobile: Top Bar with Hamburger ─────────────────────────────── */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-purple-100 sticky top-0 z-40 shadow-xs">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-xl bg-[#6D28D9] flex items-center justify-center shadow-xs">
            <GraduationCap size={15} className="text-white" />
          </div>
          <span className="text-sm font-bold text-gray-900">FeeAssist AI</span>
        </div>
        <button
          id="mobile-menu-toggle"
          type="button"
          onClick={() => setMobileOpen(true)}
          className="p-1.5 rounded-xl hover:bg-purple-50 text-purple-700 transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* ── Mobile Drawer Overlay ────────────────────────────────────────── */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="flex-1 bg-black/40 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
          <div className="w-72 bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
            <div className="flex justify-end px-4 py-3 border-b border-purple-100">
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="p-1.5 rounded-xl hover:bg-purple-50 text-gray-600"
                aria-label="Close menu"
              >
                <X size={18} />
              </button>
            </div>
            <SidebarContent />
          </div>
        </div>
      )}
    </>
  )
}
