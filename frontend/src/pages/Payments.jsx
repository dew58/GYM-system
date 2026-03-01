import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus, HiOutlineDownload } from 'react-icons/hi'

export default function Payments() {
    const [payments, setPayments] = useState([])
    const [total, setTotal] = useState(0)
    const [page, setPage] = useState(1)
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState({ member_id: '', amount: 0, method: 'cash', status: 'paid', notes: '' })

    const fetchPayments = () => {
        api.get('/payments', { params: { page, page_size: 20 } })
            .then(r => { setPayments(r.data.items); setTotal(r.data.total) }).catch(() => { })
    }
    useEffect(() => { fetchPayments() }, [page])

    const createPayment = async (e) => {
        e.preventDefault()
        try {
            await api.post('/payments', { ...form, amount: parseFloat(form.amount) })
            toast.success('Payment recorded'); setShowModal(false); fetchPayments()
        } catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const downloadReceipt = (id) => {
        const token = localStorage.getItem('access_token')
        window.open(`/api/v1/payments/${id}/receipt?token=${token}`, '_blank')
    }

    const methodColors = { cash: 'bg-success-500/20 text-success-500', card: 'bg-primary-500/20 text-primary-400', bank_transfer: 'bg-blue-500/20 text-blue-400', installment: 'bg-warning-500/20 text-warning-500' }

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h1 className="text-2xl font-bold">Payments</h1>
                <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2 w-fit">
                    <HiOutlinePlus className="w-5 h-5" /> Record Payment
                </button>
            </div>

            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Date</th><th>Member ID</th><th>Amount</th><th>Method</th><th>Status</th><th>Receipt</th><th>Actions</th></tr></thead>
                    <tbody>
                        {payments.map(p => (
                            <tr key={p.id}>
                                <td>{new Date(p.created_at).toLocaleDateString()}</td>
                                <td className="font-mono text-xs">{p.member_id?.slice(0, 8)}...</td>
                                <td className="font-semibold">{p.amount} EGP</td>
                                <td><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${methodColors[p.method]}`}>{p.method}</span></td>
                                <td className="capitalize">{p.status}</td>
                                <td className="text-xs text-surface-400">{p.receipt_number}</td>
                                <td><button onClick={() => downloadReceipt(p.id)} className="text-primary-400 hover:text-primary-300"><HiOutlineDownload className="w-4 h-4" /></button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {total > 20 && (
                <div className="flex items-center justify-center gap-2">
                    <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-secondary text-sm disabled:opacity-30">Previous</button>
                    <span className="text-sm text-surface-400">Page {page}</span>
                    <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)} className="btn-secondary text-sm disabled:opacity-30">Next</button>
                </div>
            )}

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={createPayment} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Record Payment</h3>
                        <input placeholder="Member ID" value={form.member_id} onChange={e => setForm(f => ({ ...f, member_id: e.target.value }))} className="input-field" required />
                        <input type="number" step="0.01" placeholder="Amount (EGP)" value={form.amount} onChange={e => setForm(f => ({ ...f, amount: e.target.value }))} className="input-field" required />
                        <select value={form.method} onChange={e => setForm(f => ({ ...f, method: e.target.value }))} className="input-field">
                            <option value="cash">Cash</option><option value="card">Card</option><option value="bank_transfer">Bank Transfer</option><option value="installment">Installment</option>
                        </select>
                        <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="input-field">
                            <option value="paid">Paid</option><option value="partial">Partial</option><option value="pending">Pending</option>
                        </select>
                        <textarea placeholder="Notes" value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} className="input-field" rows={2} />
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Record</button><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
