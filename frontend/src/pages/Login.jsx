import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  GraduationCap,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  CircleDollarSign,
  Bell,
  ShieldCheck,
  Sparkles,
  AlertCircle,
  MessageSquare,
  CheckCircle2,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import LiveChatShowcase from '../components/LiveChatShowcase'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const [form, setForm] = useState({ email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [loading, setLoading] = useState(false)

  const validate = () => {
    const errs = {}
    if (!form.email.trim()) {
      errs.email = 'Email is required.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errs.email = 'Enter a valid email address.'
    }
    if (!form.password) {
      errs.password = 'Password is required.'
    }
    return errs
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
    if (errors[name]) setErrors((e) => ({ ...e, [name]: undefined }))
    if (serverError) setServerError('')
  }

  const handleQuickFill = () => {
    setForm({
      email: 'demo@feeassist.ai',
      password: 'Password123!',
    })
    setErrors({})
    setServerError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError('')
    const errs = validate()
    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      return
    }

    setLoading(true)
    try {
      await login(form.email, form.password)
      const from = location.state?.from?.pathname || '/chat'
      navigate(from, { replace: true })
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        (err.response?.status === 401
          ? 'Invalid email or password. Please check your credentials.'
          : 'Unable to connect to server. Please ensure backend is running.')
      setServerError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-[#FAF8FF] relative overflow-hidden">
      {/* ── Background Ambient Blobs ────────────────────────────────────────── */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-purple-200/50 rounded-full blur-3xl pointer-events-none animate-pulse-glow" />
      <div className="absolute -bottom-32 -right-32 w-[30rem] h-[30rem] bg-violet-200/40 rounded-full blur-3xl pointer-events-none animate-pulse-glow" style={{ animationDelay: '2s' }} />

      {/* ── Left Panel (Showcase & Brand) ─────────────────────────────────── */}
      <div className="hidden lg:flex flex-col justify-center w-[50%] bg-gradient-to-br from-[#F8F4FF] via-[#F3E8FF]/60 to-[#EDE9FE]/50 px-10 xl:px-14 py-8 border-r border-purple-100/80 relative z-10">
        {/* Brand */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] flex items-center justify-center shadow-md shadow-purple-500/20 transform transition-transform hover:scale-105">
            <GraduationCap size={22} className="text-white" />
          </div>
          <div>
            <span className="text-lg font-bold bg-gradient-to-r from-[#6D28D9] to-[#4C1D95] bg-clip-text text-transparent">
              FeeAssist AI
            </span>
            <span className="block text-[11px] text-[#6B7280] font-medium tracking-tight">
              Intelligent Fees & Payments Assistant
            </span>
          </div>
        </div>

        {/* Center content */}
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/90 border border-purple-200 text-xs font-semibold text-purple-800 shadow-xs mb-3 backdrop-blur-sm">
            <Sparkles size={13} className="text-purple-600 animate-spin" style={{ animationDuration: '6s' }} />
            <span>AI Intent Engine • Multilingual • Voice Ready</span>
          </div>

          <h1 className="text-3xl font-extrabold text-[#1F2937] mb-2 leading-snug tracking-tight">
            Conversational student fees,<br />
            <span className="bg-gradient-to-r from-[#6D28D9] via-[#7C3AED] to-[#8B5CF6] bg-clip-text text-transparent">
              simplified in real time.
            </span>
          </h1>
          <p className="text-[#6B7280] text-sm mb-5 max-w-lg leading-relaxed">
            Ask questions about pending dues, scholarships, due dates, and installments in{' '}
            <strong className="text-purple-900 font-semibold">English, Hindi, or Marathi</strong> — with instant verified financial calculations.
          </p>

          {/* Dynamic Interactive Large Chat Simulator */}
          <div className="w-full">
            <LiveChatShowcase />
          </div>
        </div>
      </div>

      {/* ── Right Panel — Login Form ───────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 relative z-10">
        <div className="w-full max-w-md">
          {/* Mobile brand header */}
          <div className="flex items-center justify-between gap-3 mb-6 lg:hidden">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] flex items-center justify-center shadow-md">
                <GraduationCap size={18} className="text-white" />
              </div>
              <span className="text-base font-bold text-[#1F2937]">FeeAssist AI</span>
            </div>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 font-medium">
              Multilingual Portal
            </span>
          </div>

          {/* Form Card Container */}
          <div className="bg-white/95 backdrop-blur-md p-8 sm:p-9 rounded-3xl border border-purple-100 shadow-[0_16px_40px_rgba(109,40,217,0.08)]">
            <div className="mb-6">
              <h2 className="text-2xl font-extrabold text-[#1F2937] tracking-tight">Welcome back</h2>
              <p className="text-sm text-[#6B7280] mt-1">Sign in to check your fees and chat with AI</p>
            </div>

            {/* Quick Demo Pill */}
            <div className="mb-6 p-3.5 bg-gradient-to-r from-purple-50 via-purple-50/70 to-indigo-50 border border-purple-200/90 rounded-2xl flex items-center justify-between shadow-2xs hover:border-purple-300 transition-all">
              <div className="text-xs text-purple-900 pr-2">
                <span className="font-bold flex items-center gap-1 text-purple-950">
                  <Sparkles size={12} className="text-purple-600" />
                  Quick Demo Access
                </span>
                <span className="text-purple-700 text-[11px] block mt-0.5 font-mono">
                  demo@feeassist.ai • Password123!
                </span>
              </div>
              <button
                type="button"
                id="quick-fill-btn"
                onClick={handleQuickFill}
                className="px-3 py-1.5 text-xs font-semibold bg-[#6D28D9] hover:bg-[#5b21b6] text-white rounded-xl flex items-center gap-1.5 transition-all shadow-sm hover:scale-105 active:scale-95 flex-shrink-0"
              >
                <Sparkles size={13} />
                Auto Fill
              </button>
            </div>

            {serverError && (
              <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 flex items-start gap-2.5 text-xs text-red-700 animate-fade-in-up">
                <AlertCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
                <span>{serverError}</span>
              </div>
            )}

            <form id="login-form" onSubmit={handleSubmit} noValidate className="space-y-4">
              {/* Email */}
              <div>
                <label htmlFor="login-email" className="block text-xs font-semibold text-[#374151] mb-1.5 uppercase tracking-wider">
                  Student Email
                </label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                  <input
                    id="login-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="student@feeassist.ai"
                    className={`
                      w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border
                      text-[#1F2937] placeholder-[#9CA3AF] bg-white
                      focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/25 focus:border-[#6D28D9]
                      transition-all duration-150 shadow-2xs
                      ${errors.email ? 'border-red-400 bg-red-50/20' : 'border-[#E5E7EB] hover:border-purple-200'}
                    `}
                  />
                </div>
                {errors.email && (
                  <p className="mt-1 text-xs text-red-500">{errors.email}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label htmlFor="login-password" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider">
                    Password
                  </label>
                </div>
                <div className="relative">
                  <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••••••"
                    className={`
                      w-full pl-10 pr-10 py-2.5 text-sm rounded-xl border
                      text-[#1F2937] placeholder-[#9CA3AF] bg-white
                      focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/25 focus:border-[#6D28D9]
                      transition-all duration-150 shadow-2xs
                      ${errors.password ? 'border-red-400 bg-red-50/20' : 'border-[#E5E7EB] hover:border-purple-200'}
                    `}
                  />
                  <button
                    type="button"
                    id="toggle-password-visibility"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#6D28D9] transition-colors p-1"
                    tabIndex={-1}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-xs text-red-500">{errors.password}</p>
                )}
              </div>

              {/* Submit */}
              <button
                id="login-submit"
                type="submit"
                disabled={loading}
                className="
                  w-full flex items-center justify-center gap-2 group
                  mt-2 px-4 py-3 rounded-xl text-sm font-semibold
                  bg-gradient-to-r from-[#6D28D9] via-[#7C3AED] to-[#8B5CF6]
                  hover:from-[#5b21b6] hover:to-[#7C3AED]
                  text-white shadow-md shadow-purple-500/25
                  disabled:opacity-60 disabled:cursor-not-allowed
                  transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0
                "
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Signing in…
                  </span>
                ) : (
                  <>
                    Sign In to Portal
                    <ArrowRight size={16} className="transform transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </form>

            {/* Register link */}
            <div className="mt-6 pt-5 border-t border-gray-100 text-center">
              <p className="text-sm text-[#6B7280]">
                New student?{' '}
                <Link
                  to="/register"
                  id="go-to-register"
                  className="text-[#6D28D9] font-semibold hover:text-[#5b21b6] hover:underline transition-colors"
                >
                  Create an account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

