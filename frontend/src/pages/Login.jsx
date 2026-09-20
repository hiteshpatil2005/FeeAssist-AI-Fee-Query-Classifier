import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
  GraduationCap,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  CheckCircle2,
  CircleDollarSign,
  Bell,
  ShieldCheck,
  Sparkles,
  AlertCircle,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { icon: CircleDollarSign, text: 'Check pending fees instantly' },
  { icon: Bell,             text: 'Never miss a due date' },
  { icon: ShieldCheck,      text: 'Secure student portal' },
]

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
    <div className="min-h-screen flex bg-white">
      {/* ── Left Panel ────────────────────────────────────────────────────── */}
      <div className="hidden lg:flex flex-col justify-between w-[45%] bg-[#F9F5FF] px-12 py-12 border-r border-[#E5E7EB]">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#6D28D9] flex items-center justify-center shadow-soft-sm">
            <GraduationCap size={19} className="text-white" />
          </div>
          <span className="text-base font-semibold text-[#1F2937]">FeeAssist AI</span>
        </div>

        {/* Center content */}
        <div>
          <h1 className="text-3xl font-bold text-[#1F2937] mb-3 leading-snug">
            Your personal<br />fees assistant.
          </h1>
          <p className="text-[#6B7280] text-sm mb-8 max-w-xs leading-relaxed">
            Ask questions about your fees in English, Hindi, or Marathi — and get instant, accurate answers.
          </p>

          {/* Feature list */}
          <ul className="space-y-4">
            {FEATURES.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white border border-[#E5E7EB] flex items-center justify-center shadow-soft-sm">
                  <Icon size={16} className="text-[#6D28D9]" />
                </div>
                <span className="text-sm text-[#374151]">{text}</span>
              </li>
            ))}
          </ul>

          {/* Abstract visual preview */}
          <div className="mt-10 p-5 bg-white rounded-2xl border border-[#E5E7EB] shadow-soft max-w-xs">
            <div className="flex items-start gap-2.5 mb-3">
              <div className="w-7 h-7 rounded-full bg-[#6D28D9] flex items-center justify-center flex-shrink-0">
                <GraduationCap size={13} className="text-white" />
              </div>
              <div className="bg-[#F3E8FF] rounded-2xl rounded-tl-sm px-3 py-2 text-xs text-[#374151] leading-relaxed max-w-[200px]">
                You have ₹25,000 pending. Due date: 15 Nov 2026.
              </div>
            </div>
            <div className="flex items-start gap-2.5 flex-row-reverse">
              <div className="w-7 h-7 rounded-full bg-[#EDE9FE] flex items-center justify-center flex-shrink-0 text-xs font-semibold text-[#6D28D9]">
                S
              </div>
              <div className="bg-[#6D28D9] rounded-2xl rounded-tr-sm px-3 py-2 text-xs text-white max-w-[160px]">
                What fees do I have pending?
              </div>
            </div>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-xs text-[#9CA3AF]">
          FeeAssist AI · Multilingual Fees Assistant
        </p>
      </div>

      {/* ── Right Panel — Login Form ───────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Mobile brand */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded-xl bg-[#6D28D9] flex items-center justify-center">
              <GraduationCap size={17} className="text-white" />
            </div>
            <span className="text-base font-semibold text-[#1F2937]">FeeAssist AI</span>
          </div>

          <div className="mb-6">
            <h2 className="text-2xl font-bold text-[#1F2937] mb-1">Welcome back</h2>
            <p className="text-sm text-[#6B7280]">Sign in to your student portal account</p>
          </div>

          {/* Quick Demo Pill */}
          <div className="mb-6 p-3 bg-purple-50 border border-purple-200 rounded-xl flex items-center justify-between">
            <div className="text-xs text-purple-900">
              <span className="font-semibold block">Demo Student Credentials</span>
              <span className="text-purple-700">demo@feeassist.ai / Password123!</span>
            </div>
            <button
              type="button"
              id="quick-fill-btn"
              onClick={handleQuickFill}
              className="px-2.5 py-1 text-xs font-medium bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-1 transition-colors shadow-sm"
            >
              <Sparkles size={12} />
              Quick Fill
            </button>
          </div>

          {serverError && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
              <span>{serverError}</span>
            </div>
          )}

          <form id="login-form" onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="login-email" className="block text-sm font-medium text-[#374151] mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@college.edu"
                  className={`
                    w-full pl-9 pr-4 py-2.5 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.email ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="login-password" className="block text-sm font-medium text-[#374151] mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="login-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Your password"
                  className={`
                    w-full pl-9 pr-10 py-2.5 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.password ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
                <button
                  type="button"
                  id="toggle-password-visibility"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#6B7280]"
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
                w-full flex items-center justify-center gap-2
                px-4 py-2.5 rounded-lg text-sm font-medium
                bg-[#6D28D9] text-white
                hover:bg-[#5b21b6]
                disabled:opacity-60 disabled:cursor-not-allowed
                transition-colors duration-150
                shadow-soft-sm
              "
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Authenticating…
                </span>
              ) : (
                <>
                  Sign in
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Register link */}
          <p className="mt-6 text-center text-sm text-[#6B7280]">
            Don't have an account?{' '}
            <Link to="/register" id="go-to-register" className="text-[#6D28D9] font-medium hover:underline">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
