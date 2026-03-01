import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus } from 'react-icons/hi'

const roles = ['super_admin', 'manager', 'receptionist', 'trainer', 'accountant']

export default function Users() {
    const [users, setUsers] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState({ username: '', email: '', password: '', full_name: '', role: 'receptionist' })

    const fetch = () => api.get('/auth/users').then(r => setUsers(r.data)).catch(() => { })
    useEffect(() => { fetch() }, [])

    const create = async (e) => {
        e.preventDefault()
        try { await api.post('/auth/users', form); toast.success('User created'); setShowModal(false); fetch() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const roleColors = { super_admin: 'bg-danger-500/20 text-danger-500', manager: 'bg-primary-500/20 text-primary-400', receptionist: 'bg-success-500/20 text-success-500', trainer: 'bg-accent-500/20 text-accent-400', accountant: 'bg-warning-500/20 text-warning-500' }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">System Users</h1>
                <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2"><HiOutlinePlus className="w-5 h-5" /> Add User</button>
            </div>

            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Username</th><th>Full Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
                    <tbody>
                        {users.map(u => (
                            <tr key={u.id}>
                                <td className="font-medium">{u.username}</td><td>{u.full_name}</td><td>{u.email}</td>
                                <td><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${roleColors[u.role]}`}>{u.role.replace('_', ' ')}</span></td>
                                <td><span className={u.is_active ? 'text-success-500' : 'text-danger-500'}>{u.is_active ? 'Active' : 'Inactive'}</span></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={create} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Create User</h3>
                        <input placeholder="Username" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} className="input-field" required minLength={3} />
                        <input placeholder="Full Name" value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} className="input-field" required />
                        <input type="email" placeholder="Email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} className="input-field" required />
                        <input type="password" placeholder="Password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} className="input-field" required minLength={6} />
                        <select value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))} className="input-field">
                            {roles.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                        </select>
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Create</button><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
