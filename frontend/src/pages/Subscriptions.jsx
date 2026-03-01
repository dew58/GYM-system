import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus, HiOutlinePause, HiOutlinePlay, HiOutlineRefresh } from 'react-icons/hi'

export default function Subscriptions() {
    const [plans, setPlans] = useState([])
    const [subs, setSubs] = useState([])
    const [showPlanModal, setShowPlanModal] = useState(false)
    const [showSubModal, setShowSubModal] = useState(false)
    const [planForm, setPlanForm] = useState({ name: '', name_ar: '', duration_days: 30, price: 0, description: '' })
    const [subForm, setSubForm] = useState({ member_id: '', plan_id: '', start_date: new Date().toISOString().split('T')[0], promo_code: '' })

    const fetchData = () => {
        api.get('/subscriptions/plans').then(r => setPlans(r.data)).catch(() => { })
        api.get('/subscriptions').then(r => setSubs(r.data)).catch(() => { })
    }
    useEffect(() => { fetchData() }, [])

    const createPlan = async (e) => {
        e.preventDefault()
        try { await api.post('/subscriptions/plans', planForm); toast.success('Plan created'); setShowPlanModal(false); fetchData() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const createSub = async (e) => {
        e.preventDefault()
        try { await api.post('/subscriptions', subForm); toast.success('Subscription created'); setShowSubModal(false); fetchData() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const freezeSub = async (id) => {
        const days = prompt('Freeze for how many days?', '7')
        if (!days) return
        try { await api.post(`/subscriptions/${id}/freeze`, { freeze_days: parseInt(days) }); toast.success('Frozen'); fetchData() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const unfreezeSub = async (id) => {
        try { await api.post(`/subscriptions/${id}/unfreeze`); toast.success('Unfrozen'); fetchData() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const statusColors = { active: 'bg-success-500/20 text-success-500', expired: 'bg-danger-500/20 text-danger-500', frozen: 'bg-blue-500/20 text-blue-400', cancelled: 'bg-surface-500/20 text-surface-400' }

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h1 className="text-2xl font-bold">Subscriptions</h1>
                <div className="flex gap-2">
                    <button onClick={() => setShowPlanModal(true)} className="btn-secondary flex items-center gap-2 text-sm"><HiOutlinePlus className="w-4 h-4" /> New Plan</button>
                    <button onClick={() => setShowSubModal(true)} className="btn-primary flex items-center gap-2 text-sm"><HiOutlinePlus className="w-4 h-4" /> New Subscription</button>
                </div>
            </div>

            {/* Plans */}
            <div><h2 className="text-lg font-semibold mb-3">Plans</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {plans.map(p => (
                        <div key={p.id} className="glass-card p-4">
                            <p className="font-semibold">{p.name}</p>
                            {p.name_ar && <p className="text-xs text-surface-400">{p.name_ar}</p>}
                            <p className="text-2xl font-bold gradient-text mt-2">{p.price} EGP</p>
                            <p className="text-sm text-surface-400">{p.duration_days} days</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Subscriptions table */}
            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Member ID</th><th>Plan</th><th>Start</th><th>End</th><th>Status</th><th>Freeze Used</th><th>Actions</th></tr></thead>
                    <tbody>
                        {subs.map(s => (
                            <tr key={s.id}>
                                <td className="font-mono text-xs">{s.member_id?.slice(0, 8)}...</td>
                                <td>{plans.find(p => p.id === s.plan_id)?.name || '—'}</td>
                                <td>{s.start_date}</td><td>{s.end_date}</td>
                                <td><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[s.status]}`}>{s.status}</span></td>
                                <td>{s.freeze_days_used}/{s.max_freeze_days}</td>
                                <td className="flex gap-2">
                                    {s.status === 'active' && <button onClick={() => freezeSub(s.id)} className="text-blue-400 hover:text-blue-300" title="Freeze"><HiOutlinePause className="w-4 h-4" /></button>}
                                    {s.status === 'frozen' && <button onClick={() => unfreezeSub(s.id)} className="text-success-500 hover:text-success-600" title="Unfreeze"><HiOutlinePlay className="w-4 h-4" /></button>}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Plan Modal */}
            {showPlanModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={createPlan} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Create Plan</h3>
                        <input placeholder="Plan Name" value={planForm.name} onChange={e => setPlanForm(f => ({ ...f, name: e.target.value }))} className="input-field" required />
                        <input placeholder="Arabic Name" value={planForm.name_ar} onChange={e => setPlanForm(f => ({ ...f, name_ar: e.target.value }))} className="input-field" />
                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder="Duration (days)" value={planForm.duration_days} onChange={e => setPlanForm(f => ({ ...f, duration_days: parseInt(e.target.value) }))} className="input-field" required />
                            <input type="number" placeholder="Price (EGP)" value={planForm.price} onChange={e => setPlanForm(f => ({ ...f, price: parseFloat(e.target.value) }))} className="input-field" required />
                        </div>
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Create</button><button type="button" onClick={() => setShowPlanModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}

            {/* Subscription Modal */}
            {showSubModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={createSub} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Create Subscription</h3>
                        <input placeholder="Member ID" value={subForm.member_id} onChange={e => setSubForm(f => ({ ...f, member_id: e.target.value }))} className="input-field" required />
                        <select value={subForm.plan_id} onChange={e => setSubForm(f => ({ ...f, plan_id: e.target.value }))} className="input-field" required>
                            <option value="">Select Plan</option>
                            {plans.map(p => <option key={p.id} value={p.id}>{p.name} — {p.price} EGP</option>)}
                        </select>
                        <input type="date" value={subForm.start_date} onChange={e => setSubForm(f => ({ ...f, start_date: e.target.value }))} className="input-field" required />
                        <input placeholder="Promo Code (optional)" value={subForm.promo_code} onChange={e => setSubForm(f => ({ ...f, promo_code: e.target.value }))} className="input-field" />
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Create</button><button type="button" onClick={() => setShowSubModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
