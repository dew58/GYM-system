import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlineQrcode } from 'react-icons/hi'

export default function Attendance() {
    const [records, setRecords] = useState([])
    const [todayStats, setTodayStats] = useState(null)
    const [form, setForm] = useState({ member_id: '', barcode: '', method: 'manual' })

    const fetchData = () => {
        api.get('/attendance', { params: { page: 1, page_size: 50 } }).then(r => setRecords(r.data.items)).catch(() => { })
        api.get('/attendance/today-count').then(r => setTodayStats(r.data)).catch(() => { })
    }
    useEffect(() => { fetchData() }, [])

    const checkIn = async (e) => {
        e.preventDefault()
        const payload = { method: form.method }
        if (form.barcode) payload.barcode = form.barcode
        else payload.member_id = form.member_id
        try { await api.post('/attendance/check-in', payload); toast.success('Checked in!'); fetchData(); setForm({ member_id: '', barcode: '', method: 'manual' }) }
        catch (err) { toast.error(err.response?.data?.detail || 'Check-in failed') }
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Attendance</h1>

            {/* Today stats */}
            {todayStats && (
                <div className="grid grid-cols-2 gap-4 max-w-md">
                    <div className="glass-card p-4 text-center"><p className="text-2xl font-bold">{todayStats.total_check_ins}</p><p className="text-sm text-surface-400">Total Check-ins</p></div>
                    <div className="glass-card p-4 text-center"><p className="text-2xl font-bold">{todayStats.unique_members}</p><p className="text-sm text-surface-400">Unique Members</p></div>
                </div>
            )}

            {/* Check-in form */}
            <form onSubmit={checkIn} className="glass-card p-5 max-w-lg space-y-4">
                <h3 className="font-semibold flex items-center gap-2"><HiOutlineQrcode className="w-5 h-5" /> Quick Check-In</h3>
                <div className="grid grid-cols-2 gap-3">
                    <input placeholder="Member ID" value={form.member_id} onChange={e => setForm(f => ({ ...f, member_id: e.target.value, barcode: '' }))} className="input-field" />
                    <input placeholder="Or scan barcode" value={form.barcode} onChange={e => setForm(f => ({ ...f, barcode: e.target.value, member_id: '' }))} className="input-field" />
                </div>
                <select value={form.method} onChange={e => setForm(f => ({ ...f, method: e.target.value }))} className="input-field">
                    <option value="manual">Manual</option><option value="barcode">Barcode</option><option value="qr_code">QR Code</option>
                </select>
                <button type="submit" className="btn-primary">Check In</button>
            </form>

            {/* Attendance log */}
            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Member ID</th><th>Check-in Time</th><th>Method</th></tr></thead>
                    <tbody>
                        {records.map(r => (
                            <tr key={r.id}>
                                <td className="font-mono text-xs">{r.member_id?.slice(0, 8)}...</td>
                                <td>{new Date(r.check_in).toLocaleString()}</td>
                                <td className="capitalize">{r.method.replace('_', ' ')}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
