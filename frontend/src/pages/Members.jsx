import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus, HiOutlineSearch, HiOutlinePencil } from 'react-icons/hi'

export default function Members() {
    const [members, setMembers] = useState([])
    const [search, setSearch] = useState('')
    const [page, setPage] = useState(1)
    const [total, setTotal] = useState(0)

    const fetchMembers = () => {
        api.get('/members', { params: { page, page_size: 20, search: search || undefined } })
            .then(r => { setMembers(r.data.items); setTotal(r.data.total) })
            .catch(() => toast.error('Failed to load members'))
    }

    useEffect(() => { fetchMembers() }, [page, search])

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold">Members</h1>
                    <p className="text-surface-400 text-sm">{total} total members</p>
                </div>
                <Link to="/members/new" className="btn-primary flex items-center gap-2 w-fit">
                    <HiOutlinePlus className="w-5 h-5" /> Add Member
                </Link>
            </div>

            {/* Search */}
            <div className="relative max-w-md">
                <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input type="text" placeholder="Search by name, phone, or National ID..." value={search}
                    onChange={e => { setSearch(e.target.value); setPage(1) }}
                    className="input-field pl-10" id="member-search" />
            </div>

            {/* Table */}
            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr>
                        <th>Name</th><th>Phone</th><th>National ID</th><th>Gender</th><th>Status</th><th>Actions</th>
                    </tr></thead>
                    <tbody>
                        {members.map(m => (
                            <tr key={m.id}>
                                <td><div><p className="font-medium">{m.name_ar}</p>{m.name_en && <p className="text-xs text-surface-400">{m.name_en}</p>}</div></td>
                                <td>{m.phone}</td>
                                <td className="font-mono text-xs">{m.national_id || '—'}</td>
                                <td className="capitalize">{m.gender}</td>
                                <td><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${m.is_active ? 'bg-success-500/20 text-success-500' : 'bg-danger-500/20 text-danger-500'}`}>
                                    {m.is_active ? 'Active' : 'Inactive'}</span></td>
                                <td><Link to={`/members/${m.id}/edit`} className="text-primary-400 hover:text-primary-300">
                                    <HiOutlinePencil className="w-4 h-4" /></Link></td>
                            </tr>
                        ))}
                        {members.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-surface-400">No members found</td></tr>}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {total > 20 && (
                <div className="flex items-center justify-center gap-2">
                    <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="btn-secondary text-sm disabled:opacity-30">Previous</button>
                    <span className="text-sm text-surface-400">Page {page} of {Math.ceil(total / 20)}</span>
                    <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)} className="btn-secondary text-sm disabled:opacity-30">Next</button>
                </div>
            )}
        </div>
    )
}
