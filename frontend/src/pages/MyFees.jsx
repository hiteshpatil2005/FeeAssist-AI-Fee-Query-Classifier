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
  Plus,
  Edit2,
  Trash2,
  X,
  Calculator,
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
  const [successMsg, setSuccessMsg] = useState('')

  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingFee, setEditingFee] = useState(null)
  const [deleteConfirmId, setDeleteConfirmId] = useState(null)
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState('')

  // Form Fields
  const [formData, setFormData] = useState({
    academic_year: '2026-27',
    semester: 6,
    course: user?.course || 'B.Tech Computer Science',
    fee_type: 'Tuition',
    total_fee: 75000,
    paid_amount: 0,
    scholarship_amount: 0,
    due_date: '',
    notes: '',
  })

  // Live calculated remaining fee preview (read-only): Remaining = Total - Paid - Scholarship
  const calculatedRemaining = Math.max(
    0,
    roundTwoDecimals(
      (parseFloat(formData.total_fee) || 0) -
      (parseFloat(formData.paid_amount) || 0) -
      (parseFloat(formData.scholarship_amount) || 0)
    )
  )

  function roundTwoDecimals(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100
  }

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

  const handleOpenAdd = () => {
    setEditingFee(null)
    setFormData({
      academic_year: '2026-27',
      semester: fees.length > 0 ? Math.max(...fees.map((f) => f.semester)) + 1 : 1,
      course: user?.course || 'B.Tech Computer Science',
      fee_type: 'Tuition',
      total_fee: 75000,
      paid_amount: 0,
      scholarship_amount: 0,
      due_date: '',
      notes: '',
    })
    setFormError('')
    setIsModalOpen(true)
  }

  const handleOpenEdit = (fee) => {
    setEditingFee(fee)
    setFormData({
      academic_year: fee.academic_year,
      semester: fee.semester,
      course: fee.course || user?.course || '',
      fee_type: fee.fee_type || 'Tuition',
      total_fee: fee.total_fee,
      paid_amount: fee.paid_amount,
      scholarship_amount: fee.scholarship_amount,
      due_date: fee.due_date || '',
      notes: fee.notes || '',
    })
    setFormError('')
    setIsModalOpen(true)
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'semester' ? parseInt(value) || 1 : value,
    }))
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    setFormError('')

    const total = parseFloat(formData.total_fee)
    const paid = parseFloat(formData.paid_amount)
    const sch = parseFloat(formData.scholarship_amount)

    if (isNaN(total) || total < 0) {
      setFormError('Total Fee must be a valid positive amount.')
      return
    }
    if (isNaN(paid) || paid < 0) {
      setFormError('Paid Amount must be a valid non-negative amount.')
      return
    }
    if (isNaN(sch) || sch < 0) {
      setFormError('Scholarship Amount must be non-negative.')
      return
    }
    if (paid > total) {
      setFormError('Paid amount cannot exceed total fee.')
      return
    }

    setFormSubmitting(true)
    try {
      const payload = {
        academic_year: formData.academic_year.trim(),
        semester: Number(formData.semester),
        course: formData.course?.trim() || null,
        fee_type: formData.fee_type?.trim() || 'Tuition',
        total_fee: total,
        paid_amount: paid,
        scholarship_amount: sch,
        due_date: formData.due_date ? formData.due_date : null,
        notes: formData.notes?.trim() || null,
      }

      if (editingFee) {
        await feesService.updateFee(editingFee.id, payload)
        setSuccessMsg(`Semester ${payload.semester} fee record updated successfully!`)
      } else {
        await feesService.createFee(payload)
        setSuccessMsg(`New fee record for Semester ${payload.semester} added successfully!`)
      }
      setIsModalOpen(false)
      loadData()
      setTimeout(() => setSuccessMsg(''), 4000)
    } catch (err) {
      console.error('Failed to save fee record:', err)
      setFormError(err.response?.data?.detail || 'Failed to save fee record. Please check your inputs.')
    } finally {
      setFormSubmitting(false)
    }
  }

  const handleDelete = async (feeId) => {
    try {
      await feesService.deleteFee(feeId)
      setSuccessMsg('Fee record deleted successfully.')
      setDeleteConfirmId(null)
      loadData()
      setTimeout(() => setSuccessMsg(''), 4000)
    } catch (err) {
      console.error('Failed to delete fee record:', err)
      setError('Failed to delete fee record.')
    }
  }

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
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleOpenAdd}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-700 hover:bg-purple-800 text-xs font-semibold text-white transition-colors shadow-xs"
            >
              <Plus size={14} />
              Add Fee Record
            </button>
            <button
              type="button"
              onClick={loadData}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-medium text-slate-600 transition-colors shadow-xs"
            >
              <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-6 max-w-6xl w-full mx-auto space-y-6">
          {successMsg && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-xs text-emerald-800 animate-fadeIn">
              <CheckCircle size={16} className="text-emerald-600 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

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
                <p className="text-xs text-slate-400 mt-1 mb-4">Click below to add your first semester fee schedule.</p>
                <button
                  type="button"
                  onClick={handleOpenAdd}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-xs font-semibold text-white transition-colors"
                >
                  <Plus size={14} />
                  Add First Record
                </button>
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
                            {fee.fee_type && (
                              <span className="text-xs font-medium text-purple-700 bg-purple-50 px-2 py-0.5 rounded-md border border-purple-100">
                                {fee.fee_type}
                              </span>
                            )}
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
                          {fee.scholarship_amount > 0 && (
                            <p className="text-xs text-purple-600 font-medium">
                              Applied Scholarship: {formatCurrency(fee.scholarship_amount)}
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
                            <span className="text-[11px] text-slate-400 block uppercase">Remaining</span>
                            <span className={`text-sm font-semibold ${isCleared ? 'text-slate-400' : 'text-amber-600'}`}>
                              {formatCurrency(fee.pending_amount)}
                            </span>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 self-end md:self-center">
                          <button
                            type="button"
                            onClick={() => handleAskAboutFee(fee)}
                            className="px-3 py-1.5 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg flex items-center gap-1.5 transition-colors"
                          >
                            <Sparkles size={13} />
                            Ask FeeAssist
                          </button>
                          <button
                            type="button"
                            onClick={() => handleOpenEdit(fee)}
                            className="p-1.5 text-slate-400 hover:text-purple-700 hover:bg-slate-100 rounded-lg transition-colors"
                            title="Edit Record"
                          >
                            <Edit2 size={15} />
                          </button>
                          <button
                            type="button"
                            onClick={() => setDeleteConfirmId(fee.id)}
                            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Record"
                          >
                            <Trash2 size={15} />
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

      {/* Add / Edit Fee Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 animate-scaleIn">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-800">
                {editingFee ? `Edit Fee — Semester ${editingFee.semester}` : 'Add New Fee Record'}
              </h2>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            {formError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
                <AlertCircle size={15} className="text-red-500 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="mt-4 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Academic Year</label>
                  <input
                    type="text"
                    name="academic_year"
                    value={formData.academic_year}
                    onChange={handleFormChange}
                    placeholder="e.g. 2026-27"
                    required
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Semester (1-12)</label>
                  <input
                    type="number"
                    name="semester"
                    value={formData.semester}
                    onChange={handleFormChange}
                    min="1"
                    max="12"
                    required
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Fee Category</label>
                  <select
                    name="fee_type"
                    value={formData.fee_type}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600 bg-white"
                  >
                    <option value="Tuition">Tuition</option>
                    <option value="Hostel">Hostel</option>
                    <option value="Exam">Exam</option>
                    <option value="Mess">Mess</option>
                    <option value="Library">Library</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Due Date</label>
                  <input
                    type="date"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Total Fee (₹)</label>
                  <input
                    type="number"
                    name="total_fee"
                    value={formData.total_fee}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
                    required
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Paid Amount (₹)</label>
                  <input
                    type="number"
                    name="paid_amount"
                    value={formData.paid_amount}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
                    required
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Scholarship (₹)</label>
                  <input
                    type="number"
                    name="scholarship_amount"
                    value={formData.scholarship_amount}
                    onChange={handleFormChange}
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                  />
                </div>
              </div>

              {/* Read-Only Live Calculated Remaining Balance */}
              <div className="bg-purple-50/70 border border-purple-100 rounded-xl p-3">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5 text-purple-900 font-semibold">
                    <Calculator size={14} className="text-purple-600" />
                    <span>Calculated Remaining Balance:</span>
                  </div>
                  <span className="text-sm font-bold text-purple-950">
                    {formatCurrency(calculatedRemaining)}
                  </span>
                </div>
                <p className="text-[10px] text-purple-600/80 mt-1">
                  Formula: Remaining = Total Fee (₹{formData.total_fee || 0}) − Paid Amount (₹{formData.paid_amount || 0}) − Scholarship (₹{formData.scholarship_amount || 0})
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Notes / Remarks</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleFormChange}
                  rows="2"
                  placeholder="Optional notes or concession details..."
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-600"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-purple-700 hover:bg-purple-800 disabled:opacity-50 rounded-xl transition-colors shadow-xs"
                >
                  {formSubmitting ? 'Saving...' : editingFee ? 'Update Record' : 'Create Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-xl border border-slate-200">
            <h3 className="text-sm font-bold text-slate-800">Delete Fee Record?</h3>
            <p className="text-xs text-slate-500 mt-2">
              Are you sure you want to permanently delete this fee record? This action cannot be undone.
            </p>
            <div className="flex items-center justify-end gap-2 mt-5">
              <button
                type="button"
                onClick={() => setDeleteConfirmId(null)}
                className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleDelete(deleteConfirmId)}
                className="px-3 py-1.5 text-xs font-semibold text-white bg-red-600 hover:bg-red-700 rounded-lg"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
