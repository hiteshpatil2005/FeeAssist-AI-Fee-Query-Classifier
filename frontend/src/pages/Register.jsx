import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  GraduationCap,
  Mail,
  Lock,
  Eye,
  EyeOff,
  User,
  Globe,
  ArrowRight,
  BookOpen,
  Calendar,
  AlertCircle,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const LANGUAGES = [
  { code: 'English', label: 'English' },
  { code: 'Hindi',   label: 'Hindi — हिन्दी' },
  { code: 'Marathi', label: 'Marathi — मराठी' },
]

export default function Register() {
  const navigate = useNavigate()
  const { register, login } = useAuth()

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    preferred_language: 'English',
    course: 'B.Tech Computer Science',
    year: '3',
    semester: '5',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [loading, setLoading] = useState(false)

  const validate = () => {
    const errs = {}

    if (!form.name.trim()) {
      errs.name = 'Full name is required.'
    } else if (form.name.trim().length < 2) {
      errs.name = 'Full name must be at least 2 characters.'
    }

    if (!form.email.trim()) {
      errs.email = 'Email is required.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errs.email = 'Enter a valid email address.'
    }

    if (!form.password) {
      errs.password = 'Password is required.'
    } else if (form.password.length < 8) {
      errs.password = 'Password must be at least 8 characters.'
    }

    if (!form.confirmPassword) {
      errs.confirmPassword = 'Please confirm your password.'
    } else if (form.password !== form.confirmPassword) {
      errs.confirmPassword = 'Passwords do not match.'
    }

    return errs
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
    if (errors[name]) setErrors((err) => ({ ...err, [name]: undefined }))
    if (serverError) setServerError('')
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
      await register({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        preferred_language: form.preferred_language,
        course: form.course.trim() || undefined,
        year: form.year ? parseInt(form.year, 10) : undefined,
        semester: form.semester ? parseInt(form.semester, 10) : undefined,
      })

      // Auto login after successful registration
      await login(form.email.trim().toLowerCase(), form.password)
      navigate('/chat')
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        'Registration failed. Please check your information or try another email.'
      setServerError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F9F5FF] px-4 py-10">
      <div className="w-full max-w-lg">
        <div className="bg-white rounded-2xl border border-[#E5E7EB] shadow-soft px-8 py-8">
          {/* Brand */}
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-8 h-8 rounded-xl bg-[#6D28D9] flex items-center justify-center">
              <GraduationCap size={17} className="text-white" />
            </div>
            <span className="text-base font-semibold text-[#1F2937]">FeeAssist AI</span>
          </div>

          <div className="mb-6">
            <h1 className="text-xl font-bold text-[#1F2937] mb-1">Create student account</h1>
            <p className="text-sm text-[#6B7280]">Join to manage your college fee balances and payments.</p>
          </div>

          {serverError && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
              <span>{serverError}</span>
            </div>
          )}

          <form id="register-form" onSubmit={handleSubmit} noValidate className="space-y-4">
            {/* Full Name */}
            <div>
              <label htmlFor="register-fullname" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                Full Name
              </label>
              <div className="relative">
                <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="register-fullname"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="e.g. Aarav Sharma"
                  className={`
                    w-full pl-9 pr-4 py-2 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.name ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
              </div>
              {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name}</p>}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="register-email" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                Email address
              </label>
              <div className="relative">
                <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="register-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="student@college.edu"
                  className={`
                    w-full pl-9 pr-4 py-2 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.email ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
              </div>
              {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email}</p>}
            </div>

            {/* Course & Semester in 2 columns */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="register-course" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                  Course
                </label>
                <div className="relative">
                  <BookOpen size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                  <input
                    id="register-course"
                    name="course"
                    type="text"
                    value={form.course}
                    onChange={handleChange}
                    placeholder="B.Tech CS / MBA"
                    className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-[#E5E7EB] text-[#1F2937] bg-white focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="register-semester" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                  Semester
                </label>
                <div className="relative">
                  <Calendar size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                  <select
                    id="register-semester"
                    name="semester"
                    value={form.semester}
                    onChange={handleChange}
                    className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-[#E5E7EB] text-[#1F2937] bg-white focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                      <option key={s} value={s}>Semester {s}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="register-password" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="register-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Min. 8 characters"
                  className={`
                    w-full pl-9 pr-10 py-2 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.password ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
                <button
                  type="button"
                  id="toggle-register-password"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#6B7280]"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password}</p>}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="register-confirm-password" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF]" />
                <input
                  id="register-confirm-password"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  placeholder="Repeat your password"
                  className={`
                    w-full pl-9 pr-10 py-2 text-sm rounded-lg border
                    text-[#1F2937] placeholder-[#9CA3AF] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                    ${errors.confirmPassword ? 'border-red-400' : 'border-[#E5E7EB]'}
                  `}
                />
                <button
                  type="button"
                  id="toggle-register-confirm-password"
                  onClick={() => setShowConfirmPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#6B7280]"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-xs text-red-500">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Preferred Language */}
            <div>
              <label htmlFor="register-language" className="block text-xs font-semibold text-[#374151] uppercase tracking-wider mb-1">
                Preferred Query Language
              </label>
              <div className="relative">
                <Globe size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] pointer-events-none" />
                <select
                  id="register-language"
                  name="preferred_language"
                  value={form.preferred_language}
                  onChange={handleChange}
                  className="
                    w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-[#E5E7EB]
                    text-[#1F2937] bg-white
                    focus:outline-none focus:ring-2 focus:ring-[#6D28D9]/20 focus:border-[#6D28D9]
                    transition-colors duration-150
                  "
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>{l.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Submit */}
            <button
              id="register-submit"
              type="submit"
              disabled={loading}
              className="
                w-full flex items-center justify-center gap-2 mt-3
                px-4 py-2.5 rounded-lg text-sm font-medium
                bg-[#6D28D9] text-white
                hover:bg-[#5b21b6]
                disabled:opacity-60 disabled:cursor-not-allowed
                transition-colors duration-150 shadow-soft-sm
              "
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Creating account…
                </span>
              ) : (
                <>
                  Complete Registration
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Login link */}
          <p className="mt-5 text-center text-sm text-[#6B7280]">
            Already have an account?{' '}
            <Link to="/login" id="go-to-login" className="text-[#6D28D9] font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
