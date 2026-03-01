import { useEffect, useState } from 'react'
import api from '../api/axios'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import {
    HiOutlineUsers, HiOutlineCreditCard, HiOutlineCurrencyDollar, HiOutlineCalendar,
    HiOutlineExclamation, HiOutlineAcademicCap
} from 'react-icons/hi'

function StatCard({ icon: Icon, label, value, color, sub }) {
    const colors = {
        indigo: 'from-primary-600/20 to-primary-500/5 border-primary-500/20 text-primary-400',
        green: 'from-success-500/20 to-success-500/5 border-success-500/20 text-success-500',
        amber: 'from-warning-500/20 to-warning-500/5 border-warning-500/20 text-warning-500',
        red: 'from-danger-500/20 to-danger-500/5 border-danger-500/20 text-danger-500',
        purple: 'from-accent-500/20 to-accent-500/5 border-accent-500/20 text-accent-400',
    }
    return (
        <div className={`bg-gradient-to-br ${colors[color]} border rounded-2xl p-5 hover:scale-[1.02] transition-transform`}>
            <div className="flex items-center justify-between mb-3">
                <Icon className="w-6 h-6 opacity-80" />
                {sub && <span className="text-xs opacity-60">{sub}</span>}
            </div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-sm opacity-70 mt-1">{label}</p>
        </div>
    )
}

const chartTooltipStyle = { backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }

export default function Dashboard() {
    const [summary, setSummary] = useState(null)
    const [revenueData, setRevenueData] = useState([])
    const [attendanceData, setAttendanceData] = useState([])

    useEffect(() => {
        api.get('/dashboard/summary').then(r => setSummary(r.data)).catch(() => { })
        api.get('/dashboard/revenue-chart?months=6').then(r => setRevenueData(r.data)).catch(() => { })
        api.get('/dashboard/attendance-chart?days=14').then(r => setAttendanceData(r.data)).catch(() => { })
    }, [])

    if (!summary) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-primary-500" /></div>

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <p className="text-surface-400 text-sm">Welcome back! Here's your gym overview.</p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                <StatCard icon={HiOutlineUsers} label="Total Members" value={summary.total_members} color="indigo" />
                <StatCard icon={HiOutlineCreditCard} label="Active Subs" value={summary.active_subscriptions} color="green" />
                <StatCard icon={HiOutlineExclamation} label="Expiring Soon" value={summary.expiring_soon} color="amber" sub="7 days" />
                <StatCard icon={HiOutlineAcademicCap} label="Trainers" value={summary.total_trainers} color="purple" />
                <StatCard icon={HiOutlineCalendar} label="Today Check-ins" value={summary.today_attendance} color="indigo" />
                <StatCard icon={HiOutlineCurrencyDollar} label="Monthly Revenue" value={`${summary.monthly_revenue?.toLocaleString()} EGP`} color="green" />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Revenue Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Revenue vs Expenses</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={revenueData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                            <Tooltip contentStyle={chartTooltipStyle} />
                            <Bar dataKey="revenue" fill="#6366f1" radius={[6, 6, 0, 0]} name="Revenue (EGP)" />
                            <Bar dataKey="expenses" fill="#ef4444" radius={[6, 6, 0, 0]} name="Expenses (EGP)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                {/* Attendance Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Daily Attendance (14 days)</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <AreaChart data={attendanceData}>
                            <defs><linearGradient id="attGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient></defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                            <Tooltip contentStyle={chartTooltipStyle} />
                            <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#attGrad)" strokeWidth={2} name="Check-ins" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Quick stats row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-card p-5">
                    <p className="text-sm text-surface-400">Daily Revenue</p>
                    <p className="text-xl font-bold mt-1">{summary.daily_revenue?.toLocaleString()} EGP</p>
                </div>
                <div className="glass-card p-5">
                    <p className="text-sm text-surface-400">Monthly Revenue</p>
                    <p className="text-xl font-bold mt-1">{summary.monthly_revenue?.toLocaleString()} EGP</p>
                </div>
                <div className="glass-card p-5">
                    <p className="text-sm text-surface-400">Yearly Revenue</p>
                    <p className="text-xl font-bold mt-1">{summary.yearly_revenue?.toLocaleString()} EGP</p>
                </div>
            </div>
        </div>
    )
}
