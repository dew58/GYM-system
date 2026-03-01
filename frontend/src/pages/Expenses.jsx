import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus } from 'react-icons/hi'

const categories = ['rent', 'electricity', 'water', 'salaries', 'maintenance', 'equipment', 'supplements', 'marketing', 'cleaning', 'other']

export default function Expenses() {
    const [expenses, setExpenses] = useState([])
    const [total, setTotal] = useState(0)
    const [page, setPage] = useState(1)
    const [summary, setSummary] = useState(null)
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState({ category: 'rent', amount: 0, expense_date: new Date().toISOString().split('T')[0], description: '', vendor: '' })

    const now = new Date()
    const fetchData = () => {
        api.get('/expenses', { params: { page, page_size: 20 } }).then(r => { setExpenses(r.data.items); setTotal(r.data.total) }).catch(() => { })
        api.get('/expenses/monthly-summary', { params: { month: now.getMonth() + 1, year: now.getFullYear() } }).then(r => setSummary(r.data)).catch(() => { })
    }
    useEffect(() => { fetchData() }, [page])

    const create = async (e) => {
        e.preventDefault()
        try { await api.post('/expenses', { ...form, amount: parseFloat(form.amount) }); toast.success('Expense recorded'); setShowModal(false); fetchData() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Expenses</h1>
                <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2"><HiOutlinePlus className="w-5 h-5" /> Add Expense</button>
            </div>

            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="glass-card p-5"><p className="text-sm text-surface-400">Total Revenue</p><p className="text-xl font-bold text-success-500">{summary.total_revenue?.toLocaleString()} EGP</p></div>
                    <div className="glass-card p-5"><p className="text-sm text-surface-400">Total Expenses</p><p className="text-xl font-bold text-danger-500">{summary.total_expenses?.toLocaleString()} EGP</p></div>
                    <div className="glass-card p-5"><p className="text-sm text-surface-400">Net Profit</p><p className={`text-xl font-bold ${summary.net_profit >= 0 ? 'text-success-500' : 'text-danger-500'}`}>{summary.net_profit?.toLocaleString()} EGP</p></div>
                </div>
            )}

            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Date</th><th>Category</th><th>Amount</th><th>Description</th><th>Vendor</th></tr></thead>
                    <tbody>
                        {expenses.map(e => (
                            <tr key={e.id}>
                                <td>{e.expense_date}</td><td className="capitalize">{e.category}</td>
                                <td className="font-semibold">{e.amount} EGP</td><td>{e.description || '—'}</td><td>{e.vendor || '—'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={create} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Record Expense</h3>
                        <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} className="input-field">
                            {categories.map(c => <option key={c} value={c} className="capitalize">{c}</option>)}
                        </select>
                        <input type="number" step="0.01" placeholder="Amount (EGP)" value={form.amount} onChange={e => setForm(f => ({ ...f, amount: e.target.value }))} className="input-field" required />
                        <input type="date" value={form.expense_date} onChange={e => setForm(f => ({ ...f, expense_date: e.target.value }))} className="input-field" required />
                        <input placeholder="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} className="input-field" />
                        <input placeholder="Vendor" value={form.vendor} onChange={e => setForm(f => ({ ...f, vendor: e.target.value }))} className="input-field" />
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Record</button><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
