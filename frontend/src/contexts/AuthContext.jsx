import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (token) {
            api.get('/auth/me').then(res => { setUser(res.data); setLoading(false) })
                .catch(() => { localStorage.clear(); setLoading(false) })
        } else {
            setLoading(false)
        }
    }, [])

    const login = async (username, password) => {
        const { data } = await api.post('/auth/login', { username, password })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        setUser({ id: data.user_id, role: data.role, full_name: data.full_name })
        toast.success(`Welcome back, ${data.full_name}!`)
        return data
    }

    const logout = () => {
        localStorage.clear()
        setUser(null)
        toast.success('Logged out')
    }

    const hasRole = (...roles) => user && roles.includes(user.role)

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
