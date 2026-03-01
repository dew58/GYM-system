import { useEffect, useState } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { HiOutlinePlus, HiOutlineExclamation } from 'react-icons/hi'

const categories = ['supplement', 'equipment', 'accessory', 'apparel', 'other']

export default function Inventory() {
    const [items, setItems] = useState([])
    const [lowStock, setLowStock] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [showSaleModal, setShowSaleModal] = useState(false)
    const [form, setForm] = useState({ name: '', category: 'supplement', quantity: 0, unit_price: 0, cost_price: 0, low_stock_threshold: 5 })
    const [saleForm, setSaleForm] = useState({ item_id: '', transaction_type: 'sale', quantity: 1 })

    const fetch = () => {
        api.get('/inventory').then(r => setItems(r.data)).catch(() => { })
        api.get('/inventory/low-stock').then(r => setLowStock(r.data)).catch(() => { })
    }
    useEffect(() => { fetch() }, [])

    const create = async (e) => {
        e.preventDefault()
        try { await api.post('/inventory', { ...form, quantity: parseInt(form.quantity), unit_price: parseFloat(form.unit_price), cost_price: parseFloat(form.cost_price), low_stock_threshold: parseInt(form.low_stock_threshold) }); toast.success('Item added'); setShowModal(false); fetch() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    const recordTxn = async (e) => {
        e.preventDefault()
        try { await api.post('/inventory/transactions', { ...saleForm, quantity: parseInt(saleForm.quantity) }); toast.success('Transaction recorded'); setShowSaleModal(false); fetch() }
        catch (err) { toast.error(err.response?.data?.detail || 'Error') }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Inventory</h1>
                <div className="flex gap-2">
                    <button onClick={() => setShowSaleModal(true)} className="btn-secondary flex items-center gap-2 text-sm">Record Sale</button>
                    <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2"><HiOutlinePlus className="w-5 h-5" /> Add Item</button>
                </div>
            </div>

            {lowStock.length > 0 && (
                <div className="bg-warning-500/10 border border-warning-500/20 rounded-xl p-4 flex items-center gap-3">
                    <HiOutlineExclamation className="w-6 h-6 text-warning-500 flex-shrink-0" />
                    <div><p className="font-semibold text-warning-500">Low Stock Alert</p>
                        <p className="text-sm text-surface-300">{lowStock.map(i => i.name).join(', ')} — running low!</p></div>
                </div>
            )}

            <div className="glass-card overflow-x-auto">
                <table className="data-table">
                    <thead><tr><th>Name</th><th>Category</th><th>Qty</th><th>Price</th><th>Cost</th><th>Threshold</th></tr></thead>
                    <tbody>
                        {items.map(i => (
                            <tr key={i.id} className={i.quantity <= i.low_stock_threshold ? 'bg-warning-500/5' : ''}>
                                <td className="font-medium">{i.name}</td><td className="capitalize">{i.category}</td>
                                <td className={i.quantity <= i.low_stock_threshold ? 'text-warning-500 font-bold' : ''}>{i.quantity}</td>
                                <td>{i.unit_price} EGP</td><td>{i.cost_price || '—'} EGP</td><td>{i.low_stock_threshold}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={create} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Add Inventory Item</h3>
                        <input placeholder="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="input-field" required />
                        <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} className="input-field">{categories.map(c => <option key={c} value={c}>{c}</option>)}</select>
                        <div className="grid grid-cols-2 gap-3">
                            <input type="number" placeholder="Quantity" value={form.quantity} onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} className="input-field" />
                            <input type="number" step="0.01" placeholder="Sell Price" value={form.unit_price} onChange={e => setForm(f => ({ ...f, unit_price: e.target.value }))} className="input-field" required />
                            <input type="number" step="0.01" placeholder="Cost Price" value={form.cost_price} onChange={e => setForm(f => ({ ...f, cost_price: e.target.value }))} className="input-field" />
                            <input type="number" placeholder="Low Stock Threshold" value={form.low_stock_threshold} onChange={e => setForm(f => ({ ...f, low_stock_threshold: e.target.value }))} className="input-field" />
                        </div>
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Add</button><button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}

            {showSaleModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
                    <form onSubmit={recordTxn} className="glass-card p-6 w-full max-w-md space-y-4">
                        <h3 className="text-lg font-bold">Record Transaction</h3>
                        <select value={saleForm.item_id} onChange={e => setSaleForm(f => ({ ...f, item_id: e.target.value }))} className="input-field" required>
                            <option value="">Select Item</option>{items.map(i => <option key={i.id} value={i.id}>{i.name} (qty: {i.quantity})</option>)}
                        </select>
                        <select value={saleForm.transaction_type} onChange={e => setSaleForm(f => ({ ...f, transaction_type: e.target.value }))} className="input-field">
                            <option value="sale">Sale</option><option value="purchase">Purchase</option><option value="return">Return</option><option value="adjustment">Adjustment</option>
                        </select>
                        <input type="number" placeholder="Quantity" value={saleForm.quantity} onChange={e => setSaleForm(f => ({ ...f, quantity: e.target.value }))} className="input-field" required />
                        <div className="flex gap-2"><button type="submit" className="btn-primary">Record</button><button type="button" onClick={() => setShowSaleModal(false)} className="btn-secondary">Cancel</button></div>
                    </form>
                </div>
            )}
        </div>
    )
}
