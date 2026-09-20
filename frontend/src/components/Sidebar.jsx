import { useState } from 'react'
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
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { id: 'chat',            label: 'Chat Assistant',  icon: MessageSquare, path: '/chat' },
  { id: 'my-fees',         label: 'My Fees',         icon: Receipt,       path: '/fees' },
  { id: 'payment-history', label: 'Payment History', icon: Clock,         path: '/payments' },
  { id: 'profile',         label: 'Student Profile', icon: User,          path: '/profile' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

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

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-[#E5E7EB]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#6D28D9] flex items-center justify-center flex-shrink-0 shadow-soft-sm">
            <GraduationCap size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-[#1F2937] leading-tight">FeeAssist AI</p>
            <p className="text-[10px] text-[#6B7280] leading-tight">Student Portal</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
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
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                text-sm font-medium text-left
                transition-all duration-150
                ${active
                  ? 'bg-purple-50 text-purple-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }
              `}
            >
              <Icon size={18} className={active ? 'text-purple-600' : 'text-slate-400'} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      {/* User Footer */}
      <div className="px-3 py-4 border-t border-[#E5E7EB] bg-slate-50/50">
        <div className="flex items-center gap-3 px-2 mb-3">
          <div className="w-9 h-9 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 text-sm font-bold text-purple-700 border border-purple-200 shadow-xs">
            {initial}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-800 truncate">{userName}</p>
            <p className="text-[11px] text-slate-500 truncate">{userEmail}</p>
          </div>
        </div>
        <button
          id="logout-button"
          type="button"
          onClick={handleLogout}
          className="
            w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium
            text-slate-600 hover:text-red-600 hover:bg-red-50
            transition-colors duration-150
          "
        >
          <LogOut size={15} />
          Sign out
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* ── Desktop Sidebar ─────────────────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-64 flex-shrink-0 bg-white border-r border-[#E5E7EB] h-screen sticky top-0">
        <SidebarContent />
      </aside>

      {/* ── Mobile: top bar with hamburger ─────────────────────────────── */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-[#E5E7EB] sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#6D28D9] flex items-center justify-center">
            <GraduationCap size={15} className="text-white" />
          </div>
          <span className="text-sm font-bold text-slate-800">FeeAssist AI</span>
        </div>
        <button
          id="mobile-menu-toggle"
          type="button"
          onClick={() => setMobileOpen(true)}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-slate-600"
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* ── Mobile Drawer Overlay ────────────────────────────────────────── */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="flex-1 bg-black/40 backdrop-blur-xs"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
          <div className="w-72 bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
            <div className="flex justify-end px-4 py-3 border-b border-[#E5E7EB]">
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-slate-600"
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
