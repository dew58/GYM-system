import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus } from 'react-icons/hi'

export default function Trainers() {
    const [trainers, setTrainers] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState({ name: '', phone: '', specialization: '', commission_rate: 0, salary: 0 })

    const fetch = () => api.get('/trainers').then(r => setTrainers(r.data)).catch(() => { })
    useEffect(() => { fetch() }, [])

    const create = async (e) => {
        e.preventDefault()
        try { await api.post('/trainers', { ...form, commission_rate: parseFloat(form.commission_rate), salary: parseFloat(form.salary) }); toast.success('Trainer added'); setShowModal(false); fetch() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Trainers</h1>
                <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2"><HiOutlinePlus className="w-5 h-5" /> Add Trainer</button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trainers.map(t => (
                    <div key={t.id} className="glass-card p-5">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-500 to-primary-500 flex items-center justify-center font-bold">{t.name[0]}</div>
                            <div><p className="font-semibold">{t.name}</p><p className="text-xs text-surface-400">{t.specialization || 'General'}</p></div>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                            <div><p className="text-surface-400">Phone</p><p>{t.phone || '—'}</p></div>
                            <div><p className="text-surface-400">Salary</p><p>{t.salary} EGP</p></div>
                            <div><p className="text-surface-400">Commission</p><p>{t.commission_rate}%</p></div>
                            <div><p className="text-surface-400">Status</p><p className={t.is_active ? 'text-success-500' : 'text-danger-500'}>{t.is_active ? 'Active' : 'Inactive'}</p></div>
                        </div>
                    </div>
                ))}
            </div>
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={create} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Add Trainer</h3>
                        <input placeholder="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="input-field" required />
                        <input placeholder="Phone" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} className="input-field" />
                        <input placeholder="Specialization" value={form.specialization} onChange={e => setForm(f => ({ ...f, specialization: e.target.value }))} className="input-field" />
                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" step="0.01" placeholder="Salary (EGP)" value={form.salary} onChange={e => setForm(f => ({ ...f, salary: e.target.value }))} className="input-field" />
                            <input type="number" step="0.01" placeholder="Commission %" value={form.commission_rate} onChange={e => setForm(f => ({ ...f, commission_rate: e.target.value }))} className="input-field" />
                        </div>
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Add</button><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
