import { useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlineDownload } from 'react-icons/hi'

export default function Reports() {
    const [month, setMonth] = useState(new Date().getMonth() + 1)
    const [year, setYear] = useState(new Date().getFullYear())

    const download = async (type) => {
        try {
            let url = ''
            if (type === 'members') url = '/reports/members/export'
            else if (type === 'financial') url = `/reports/financial/export?month=${month}&year=${year}`
            else if (type === 'attendance') {
                const from = `${year}-${String(month).padStart(2, '0')}-01`
                const lastDay = new Date(year, month, 0).getDate()
                const to = `${year}-${String(month).padStart(2, '0')}-${lastDay}`
                url = `/reports/attendance/export?date_from=${from}&date_to=${to}`
            }
            const res = await api.get(url, { responseType: 'blob' })
            const blob = new Blob([res.data])
            const link = document.createElement('a'); link.href = URL.createObjectURL(blob)
            link.download = `${type}_report.xlsx`; link.click()
            toast.success('Report downloaded')
        } catch { toast.error('Failed to download report') }
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Reports & Export</h1>

            {/* Filters */}
            <div className="glass-card p-5 flex flex-wrap items-end gap-4">
                <div>
                    <label className="block text-sm text-surface-400 mb-1">Month</label>
                    <select value={month} onChange={e => setMonth(parseInt(e.target.value))} className="input-field w-32">
                        {Array.from({ length: 12 }, (_, i) => <option key={i} value={i + 1}>{new Date(2000, i).toLocaleString('default', { month: 'long' })}</option>)}
                    </select>
                </div>
                <div>
                    <label className="block text-sm text-surface-400 mb-1">Year</label>
                    <input type="number" value={year} onChange={e => setYear(parseInt(e.target.value))} className="input-field w-28" />
                </div>
            </div>

            {/* Report Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                    { type: 'members', title: 'Members Report', desc: 'Export all members with details', color: 'primary' },
                    { type: 'financial', title: 'Financial Report', desc: 'Revenue, expenses, and net profit', color: 'green' },
                    { type: 'attendance', title: 'Attendance Report', desc: 'Monthly attendance records', color: 'purple' },
                ].map(r => (
                    <div key={r.type} className="glass-card p-6 flex flex-col items-start">
                        <h3 className="text-lg font-semibold mb-1">{r.title}</h3>
                        <p className="text-sm text-surface-400 mb-4">{r.desc}</p>
                        <button onClick={() => download(r.type)} className="btn-primary text-sm flex items-center gap-2 mt-auto">
                            <HiOutlineDownload className="w-4 h-4" /> Download Excel
                        </button>
                    </div>
                ))}
            </div>
        </div>
    )
}
