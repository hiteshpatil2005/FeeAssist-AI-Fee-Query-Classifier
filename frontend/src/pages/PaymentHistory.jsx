import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Clock,
  CheckCircle2,
  Download,
  AlertCircle,
  RefreshCw,
  Sparkles,
  CreditCard,
  FileText,
} from 'lucide-react'
import Sidebar from '../components/Sidebar'
import { paymentsService } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function PaymentHistory() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [receiptModal, setReceiptModal] = useState(null)

  const loadPayments = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await paymentsService.getPayments()
      setPayments(res.data)
    } catch (err) {
      console.error('Failed to load payments:', err)
      setError('Unable to load payment records. Please verify connection.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPayments()
  }, [])

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val || 0)
  }

  const totalPaid = payments.reduce((acc, p) => acc + (parseFloat(p.amount) || 0), 0)

  return (
    <div className="flex flex-col md:flex-row h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar />

      <main className="flex-1 flex flex-col h-full overflow-y-auto">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-5 sticky top-0 z-10 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">Payment History & Receipts</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Verified transaction receipts for fees submitted online or offline
            </p>
          </div>
          <button
            type="button"
            onClick={loadPayments}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-medium text-slate-600 transition-colors shadow-xs"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </header>

        {/* Content */}
        <div className="p-6 max-w-6xl w-full mx-auto space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between text-xs text-red-700">
              <div className="flex items-center gap-2">
                <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
                <span>{error}</span>
              </div>
              <button
                type="button"
                onClick={loadPayments}
                className="font-semibold underline hover:text-red-900 ml-4"
              >
                Retry
              </button>
            </div>
          )}

          {/* Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Recorded Payments</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                  <CreditCard size={16} />
                </div>
              </div>
              <div className="text-2xl font-bold text-emerald-600">
                {formatCurrency(totalPaid)}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">{payments.length} transactions completed</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Primary Payment Mode</span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
                  <CheckCircle2 size={16} />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-800">
                UPI / Net Banking
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Instant digital clearance</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-soft flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Assistant Query</span>
                <p className="text-xs text-slate-600 mt-1">Need receipt reconciliation?</p>
              </div>
              <button
                type="button"
                onClick={() => navigate('/chat', { state: { initialQuery: 'When did I make my last payment?' } })}
                className="mt-3 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Sparkles size={13} />
                Ask when I last paid
              </button>
            </div>
          </div>

          {/* Transactions List */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-soft overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-800">Payment Transactions</h3>
              <span className="text-xs font-medium text-slate-500">Student ID: {user?.id}</span>
            </div>

            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading transactions...</div>
            ) : payments.length === 0 ? (
              <div className="p-12 text-center">
                <Clock size={36} className="mx-auto text-slate-300 mb-2" />
                <p className="text-sm font-medium text-slate-600">No payment transactions found.</p>
                <p className="text-xs text-slate-400 mt-1">Payments made through the college portal will automatically appear here.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-[11px] uppercase tracking-wider text-slate-500 font-semibold">
                      <th className="py-3.5 px-6">Transaction Ref</th>
                      <th className="py-3.5 px-6">Fee Category</th>
                      <th className="py-3.5 px-6">Payment Mode</th>
                      <th className="py-3.5 px-6">Date</th>
                      <th className="py-3.5 px-6">Amount</th>
                      <th className="py-3.5 px-6">Status</th>
                      <th className="py-3.5 px-6 text-right">Receipt</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                    {payments.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="py-4 px-6 font-mono font-medium text-slate-800">
                          {p.transaction_id || `REF-${p.id}`}
                        </td>
                        <td className="py-4 px-6 font-medium text-slate-900">
                          {p.fee_type}
                        </td>
                        <td className="py-4 px-6 text-slate-600">
                          {p.payment_method}
                        </td>
                        <td className="py-4 px-6 text-slate-600">
                          {p.payment_date}
                        </td>
                        <td className="py-4 px-6 font-bold text-emerald-600">
                          {formatCurrency(p.amount)}
                        </td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            <CheckCircle2 size={11} />
                            {p.status || 'Completed'}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-right">
                          <button
                            type="button"
                            onClick={() => setReceiptModal(p)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 text-slate-600 hover:text-purple-700 hover:bg-purple-50 rounded-lg transition-colors text-xs font-medium"
                          >
                            <FileText size={13} />
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Receipt Modal */}
        {receiptModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-150">
              <div className="p-6 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Official Fee Receipt</h4>
                  <p className="text-xs text-slate-500">Transaction #{receiptModal.transaction_id || receiptModal.id}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setReceiptModal(null)}
                  className="text-slate-400 hover:text-slate-600 text-sm font-semibold"
                >
                  ✕
                </button>
              </div>
              <div className="p-6 space-y-4 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Student Name</span>
                  <span className="font-semibold text-slate-800">{user?.name}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Student Email</span>
                  <span className="font-semibold text-slate-800">{user?.email}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Payment Category</span>
                  <span className="font-semibold text-slate-800">{receiptModal.fee_type}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Mode of Payment</span>
                  <span className="font-semibold text-slate-800">{receiptModal.payment_method}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Payment Date</span>
                  <span className="font-semibold text-slate-800">{receiptModal.payment_date}</span>
                </div>
                <div className="flex justify-between py-2 bg-purple-50/70 px-3 rounded-lg">
                  <span className="font-bold text-purple-900">Amount Paid</span>
                  <span className="font-bold text-purple-900 text-sm">{formatCurrency(receiptModal.amount)}</span>
                </div>
              </div>
              <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="px-3.5 py-1.5 text-xs font-semibold bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-1.5 transition-colors shadow-xs"
                >
                  <Download size={13} />
                  Print Receipt
                </button>
                <button
                  type="button"
                  onClick={() => setReceiptModal(null)}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
