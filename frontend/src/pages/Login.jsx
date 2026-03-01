import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            await login(username, password)
            navigate('/')
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-surface-900 relative overflow-hidden">
            {/* Background effects */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent-500/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2" />

            <div className="relative w-full max-w-md mx-4">
                <div className="glass-card p-8">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4 shadow-lg shadow-primary-500/30">
                            <span className="text-3xl">💪</span>
                        </div>
                        <h1 className="text-2xl font-bold gradient-text">GYM PRO</h1>
                        <p className="text-surface-400 mt-1 text-sm">Management System</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-surface-300 mb-1.5">Username</label>
                            <input id="login-username" type="text" value={username} onChange={e => setUsername(e.target.value)}
                                className="input-field" placeholder="Enter your username" required />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-surface-300 mb-1.5">Password</label>
                            <input id="login-password" type="password" value={password} onChange={e => setPassword(e.target.value)}
                                className="input-field" placeholder="Enter your password" required />
                        </div>
                        <button id="login-submit" type="submit" disabled={loading}
                            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50">
                            {loading ? <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white" /> : null}
                            {loading ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>

                    <p className="text-center text-xs text-surface-500 mt-6">
                        Default: admin / Admin@123
                    </p>
                </div>
            </div>
        </div>
    )
}
