import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import toast from 'react-hot-toast'

export default function MemberForm() {
    const { id } = useParams()
    const navigate = useNavigate()
    const isEdit = Boolean(id)
    const [form, setForm] = useState({
        name_ar: '', name_en: '', national_id: '', phone: '', emergency_contact: '',
        email: '', gender: 'male', date_of_birth: '', medical_notes: '', address: ''
    })
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (isEdit) api.get(`/members/${id}`).then(r => {
            const d = r.data; setForm({
                name_ar: d.name_ar, name_en: d.name_en || '', national_id: d.national_id || '',
                phone: d.phone, emergency_contact: d.emergency_contact || '', email: d.email || '',
                gender: d.gender, date_of_birth: d.date_of_birth || '', medical_notes: d.medical_notes || '',
                address: d.address || ''
            })
        })
    }, [id])

    const handleSubmit = async (e) => {
        e.preventDefault(); setLoading(true)
        try {
            const payload = { ...form }
            if (!payload.national_id) delete payload.national_id
            if (!payload.date_of_birth) delete payload.date_of_birth
            if (isEdit) await api.put(`/members/${id}`, payload)
            else await api.post('/members', payload)
            toast.success(isEdit ? 'Member updated' : 'Member created')
            navigate('/members')
        } catch (err) { toast.error(err.response?.data?.detail || 'Error saving member') }
        finally { setLoading(false) }
    }

    const Field = ({ label, name, type = 'text', required, ...props }) => (
        <div>
            <label className="block text-sm font-medium text-surface-300 mb-1">{label}{required && <span className="text-danger-500 ml-1">*</span>}</label>
            <input type={type} value={form[name]} onChange={e => setForm(f => ({ ...f, [name]: e.target.value }))}
                className="input-field" required={required} {...props} />
        </div>
    )

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold">{isEdit ? 'Edit Member' : 'Add New Member'}</h1>
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Field label="Arabic Name (الاسم بالعربي)" name="name_ar" required />
                    <Field label="English Name" name="name_en" />
                    <Field label="National ID (الرقم القومي)" name="national_id" maxLength={14} placeholder="14 digits" />
                    <Field label="Phone" name="phone" required placeholder="+20 1xx xxxx xxx" />
                    <Field label="Emergency Contact" name="emergency_contact" />
                    <Field label="Email" name="email" type="email" />
                    <div>
                        <label className="block text-sm font-medium text-surface-300 mb-1">Gender <span className="text-danger-500">*</span></label>
                        <select value={form.gender} onChange={e => setForm(f => ({ ...f, gender: e.target.value }))} className="input-field">
                            <option value="male">Male</option><option value="female">Female</option>
                        </select>
                    </div>
                    <Field label="Date of Birth" name="date_of_birth" type="date" />
                </div>
                <Field label="Address" name="address" />
                <div>
                    <label className="block text-sm font-medium text-surface-300 mb-1">Medical Notes</label>
                    <textarea value={form.medical_notes} onChange={e => setForm(f => ({ ...f, medical_notes: e.target.value }))}
                        className="input-field" rows={3} placeholder="Any medical conditions, injuries, etc." />
                </div>
                <div className="flex gap-3 pt-2">
                    <button type="submit" disabled={loading} className="btn-primary disabled:opacity-50">
                        {loading ? 'Saving...' : isEdit ? 'Update Member' : 'Create Member'}
                    </button>
                    <button type="button" onClick={() => navigate('/members')} className="btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    )
}
