import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Receipt,
  CheckCircle,
  AlertCircle,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Award,
} from 'lucide-react'
import Sidebar from '../components/Sidebar'
import { feesService } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function MyFees() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [fees, setFees] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [feesRes, summaryRes] = await Promise.all([
        feesService.getFees(),
        feesService.getSummary(),
      ])
      setFees(feesRes.data)
      setSummary(summaryRes.data)
    } catch (err) {
      console.error('Failed to load fees:', err)
      setError('Unable to load fee details from server. Please verify your connection.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleAskAboutFee = (fee) => {
    navigate('/chat', {
      state: {
        initialQuery: `What is my pending balance for semester ${fee.semester}?`,
      },
    })
  }

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val || 0)
  }

  return (
    <div className="flex flex-col md:flex-row h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar />

      <main className="flex-1 flex flex-col h-full overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-5 sticky top-0 z-10 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">My College Fees</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Personal fee structure, payment status, and upcoming deadlines
            </p>
          </div>
          <button
            type="button"
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-medium text-slate-600 transition-colors shadow-xs"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </header>

        {/* Content Area */}
        <div className="p-6 max-w-6xl w-full mx-auto space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between text-xs text-red-700">
              <div className="flex items-center gap-2">
                <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
                <span>{error}</span>
              </div>
              <button
                type="button"
                onClick={loadData}
                className="font-semibold underline hover:text-red-900 ml-4"
              >
                Retry
              </button>
            </div>
          )}

          {/* Fee Summary Cards */}
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-28 bg-white rounded-2xl border border-slate-200 animate-pulse" />
              ))}
            </div>
          ) : summary ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Total Fees */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Fees</span>
                  <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
                    <Receipt size={16} />
                  </div>
                </div>
                <div className="text-2xl font-bold text-slate-800">
                  {formatCurrency(summary.total_fee)}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Total curriculum charges</p>
              </div>

              {/* Total Paid */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Paid</span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                    <CheckCircle size={16} />
                  </div>
                </div>
                <div className="text-2xl font-bold text-emerald-600">
                  {formatCurrency(summary.paid_amount)}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Cleared installments</p>
              </div>

              {/* Total Pending */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Due</span>
                  <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
                    <Clock size={16} />
                  </div>
                </div>
                <div className={`text-2xl font-bold ${summary.pending_amount > 0 ? 'text-amber-600' : 'text-slate-800'}`}>
                  {formatCurrency(summary.pending_amount)}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Outstanding balance</p>
              </div>

              {/* Scholarship */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Scholarship</span>
                  <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
                    <Award size={16} />
                  </div>
                </div>
                <div className="text-2xl font-bold text-purple-600">
                  {formatCurrency(summary.scholarship_amount)}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Financial aid applied</p>
              </div>
            </div>
          ) : null}

          {/* Quick AI Assistant Banner */}
          <div className="bg-linear-to-r from-purple-700 to-indigo-800 rounded-2xl p-6 text-white shadow-soft flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <Sparkles size={18} className="text-purple-200" />
                <h2 className="text-base font-bold">Have questions about your fee breakdown?</h2>
              </div>
              <p className="text-xs text-purple-100 max-w-xl">
                FeeAssist AI can calculate installment dates, explain scholarship criteria, or check previous semester receipts in English, Hindi, or Marathi.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="px-4 py-2 bg-white text-purple-800 hover:bg-purple-50 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shrink-0 shadow-sm"
            >
              Ask AI Assistant
              <ArrowRight size={14} />
            </button>
          </div>

          {/* Semester Breakdown Section */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-soft overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Semester-wise Breakdown</h3>
                <p className="text-xs text-slate-500">Student: {user?.name} · {user?.course || 'Degree Program'}</p>
              </div>
              <span className="text-xs font-medium text-purple-700 bg-purple-50 px-2.5 py-1 rounded-full border border-purple-100">
                {fees.length} Records Found
              </span>
            </div>

            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading fee records...</div>
            ) : fees.length === 0 ? (
              <div className="p-12 text-center">
                <Receipt size={36} className="mx-auto text-slate-300 mb-2" />
                <p className="text-sm font-medium text-slate-600">No fee records found for this account.</p>
                <p className="text-xs text-slate-400 mt-1">If this is a new account, fee schedules may be added by administration soon.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {fees.map((fee) => {
                  const percentPaid = fee.total_fee > 0 ? Math.min(100, Math.round((fee.paid_amount / fee.total_fee) * 100)) : 0
                  const isCleared = fee.pending_amount <= 0

                  return (
                    <div key={fee.id} className="p-6 hover:bg-slate-50/60 transition-colors">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        {/* Title and metadata */}
                        <div className="space-y-1">
                          <div className="flex items-center gap-2.5">
                            <span className="text-base font-bold text-slate-800">
                              Semester {fee.semester}
                            </span>
                            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                              AY {fee.academic_year}
                            </span>
                            {isCleared ? (
                              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                                Fully Paid
                              </span>
                            ) : (
                              <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                                {formatCurrency(fee.pending_amount)} Due
                              </span>
                            )}
                          </div>
                          {fee.due_date && (
                            <p className="text-xs text-slate-500">
                              Due Date: <span className="font-medium text-slate-700">{fee.due_date}</span>
                            </p>
                          )}
                        </div>

                        {/* Financial Figures */}
                        <div className="grid grid-cols-3 gap-6 text-right md:text-left">
                          <div>
                            <span className="text-[11px] text-slate-400 block uppercase">Total</span>
                            <span className="text-sm font-semibold text-slate-800">{formatCurrency(fee.total_fee)}</span>
                          </div>
                          <div>
                            <span className="text-[11px] text-slate-400 block uppercase">Paid</span>
                            <span className="text-sm font-semibold text-emerald-600">{formatCurrency(fee.paid_amount)}</span>
                          </div>
                          <div>
                            <span className="text-[11px] text-slate-400 block uppercase">Pending</span>
                            <span className={`text-sm font-semibold ${isCleared ? 'text-slate-400' : 'text-amber-600'}`}>
                              {formatCurrency(fee.pending_amount)}
                            </span>
                          </div>
                        </div>

                        {/* Action */}
                        <div className="flex items-center gap-2 self-end md:self-center">
                          <button
                            type="button"
                            onClick={() => handleAskAboutFee(fee)}
                            className="px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg flex items-center gap-1.5 transition-colors"
                          >
                            <Sparkles size={13} />
                            Query Fee
                          </button>
                        </div>
                      </div>

                      {/* Progress bar */}
                      <div className="mt-4">
                        <div className="flex justify-between text-[11px] text-slate-500 mb-1">
                          <span>Payment Progress</span>
                          <span className="font-semibold">{percentPaid}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${isCleared ? 'bg-emerald-500' : 'bg-purple-600'}`}
                            style={{ width: `${percentPaid}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
