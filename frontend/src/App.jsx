import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Members from './pages/Members'
import MemberForm from './pages/MemberForm'
import Subscriptions from './pages/Subscriptions'
import Payments from './pages/Payments'
import Trainers from './pages/Trainers'
import Attendance from './pages/Attendance'
import Expenses from './pages/Expenses'
import Inventory from './pages/Inventory'
import Reports from './pages/Reports'
import Users from './pages/Users'

function ProtectedRoute({ children, roles }) {
    const { user, loading } = useAuth()
    if (loading) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary-500"></div></div>
    if (!user) return <Navigate to="/login" />
    if (roles && !roles.includes(user.role)) return <Navigate to="/" />
    return children
}

export default function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route index element={<Dashboard />} />
                <Route path="members" element={<Members />} />
                <Route path="members/new" element={<MemberForm />} />
                <Route path="members/:id/edit" element={<MemberForm />} />
                <Route path="subscriptions" element={<Subscriptions />} />
                <Route path="payments" element={<Payments />} />
                <Route path="trainers" element={<Trainers />} />
                <Route path="attendance" element={<Attendance />} />
                <Route path="expenses" element={<ProtectedRoute roles={['super_admin', 'manager', 'accountant']}><Expenses /></ProtectedRoute>} />
                <Route path="inventory" element={<Inventory />} />
                <Route path="reports" element={<ProtectedRoute roles={['super_admin', 'manager', 'accountant']}><Reports /></ProtectedRoute>} />
                <Route path="users" element={<ProtectedRoute roles={['super_admin']}><Users /></ProtectedRoute>} />
            </Route>
        </Routes>
    )
}
