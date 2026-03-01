import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useState } from 'react'
import {
    HiOutlineHome, HiOutlineUsers, HiOutlineCreditCard, HiOutlineClipboardList, HiOutlineCalendar,
    HiOutlineCurrencyDollar, HiOutlineCube, HiOutlineChartBar, HiOutlineCog, HiOutlineLogout,
    HiOutlineMenu, HiOutlineX, HiOutlineAcademicCap
} from 'react-icons/hi'

const navItems = [
    { to: '/', icon: HiOutlineHome, label: 'Dashboard', roles: ['super_admin', 'manager', 'accountant'] },
    { to: '/members', icon: HiOutlineUsers, label: 'Members' },
    { to: '/subscriptions', icon: HiOutlineCreditCard, label: 'Subscriptions' },
    { to: '/payments', icon: HiOutlineCurrencyDollar, label: 'Payments' },
    { to: '/trainers', icon: HiOutlineAcademicCap, label: 'Trainers', roles: ['super_admin', 'manager'] },
    { to: '/attendance', icon: HiOutlineCalendar, label: 'Attendance' },
    { to: '/expenses', icon: HiOutlineClipboardList, label: 'Expenses', roles: ['super_admin', 'manager', 'accountant'] },
    { to: '/inventory', icon: HiOutlineCube, label: 'Inventory' },
    { to: '/reports', icon: HiOutlineChartBar, label: 'Reports', roles: ['super_admin', 'manager', 'accountant'] },
    { to: '/users', icon: HiOutlineCog, label: 'Users', roles: ['super_admin'] },
]

export default function Layout() {
    const { user, logout, hasRole } = useAuth()
    const navigate = useNavigate()
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const handleLogout = () => { logout(); navigate('/login') }

    const filteredNav = navItems.filter(item => !item.roles || item.roles.includes(user?.role))

    const SidebarContent = () => (
        <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="p-6 border-b border-white/10">
                <h1 className="text-xl font-bold gradient-text">💪 GYM PRO</h1>
                <p className="text-xs text-surface-400 mt-1">Management System</p>
            </div>
            {/* Nav */}
            <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                {filteredNav.map(item => (
                    <NavLink key={item.to} to={item.to} end={item.to === '/'}
                        onClick={() => setSidebarOpen(false)}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${isActive ? 'bg-primary-600/20 text-primary-400 shadow-lg shadow-primary-500/10' : 'text-surface-300 hover:bg-white/5 hover:text-white'}`}>
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>
            {/* User info + logout */}
            <div className="p-4 border-t border-white/10">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-sm font-bold">
                        {user?.full_name?.[0] || 'A'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{user?.full_name || 'Admin'}</p>
                        <p className="text-xs text-surface-400 capitalize">{user?.role?.replace('_', ' ')}</p>
                    </div>
                </div>
                <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-surface-400 hover:text-danger-500 w-full px-2 py-1.5 rounded-lg hover:bg-white/5">
                    <HiOutlineLogout className="w-4 h-4" /> Logout
                </button>
            </div>
        </div>
    )

    return (
        <div className="flex h-screen overflow-hidden bg-surface-900">
            {/* Desktop sidebar */}
            <aside className="hidden lg:flex lg:w-64 flex-col bg-surface-800/50 border-r border-white/5">
                <SidebarContent />
            </aside>
            {/* Mobile sidebar overlay */}
            {sidebarOpen && (
                <div className="fixed inset-0 z-50 flex lg:hidden">
                    <div className="fixed inset-0 bg-black/60" onClick={() => setSidebarOpen(false)} />
                    <div className="relative w-64 bg-surface-800 shadow-2xl z-50"><SidebarContent /></div>
                </div>
            )}
            {/* Main area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top navbar */}
                <header className="h-16 border-b border-white/5 bg-surface-800/30 backdrop-blur-xl flex items-center justify-between px-6">
                    <button className="lg:hidden text-surface-300 hover:text-white" onClick={() => setSidebarOpen(true)}>
                        <HiOutlineMenu className="w-6 h-6" />
                    </button>
                    <div className="flex items-center gap-4 ml-auto">
                        <span className="text-sm text-surface-400">
                            {new Date().toLocaleDateString('en-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        </span>
                    </div>
                </header>
                {/* Page content */}
                <main className="flex-1 overflow-y-auto p-6"><Outlet /></main>
            </div>
        </div>
    )
}
