import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function SellersCRUD() {
  const { token } = useAuth()
  const [sellers, setSellers] = useState([])
  const [form, setForm] = useState({ company_name: '', contact_name: '', seller_email: '' })
  const load = () => apiRequest('/admin/sellers', { token }).then(setSellers)
  useEffect(load, [token])

  async function create() {
    await apiRequest('/admin/sellers', { method: 'POST', token, body: form })
    setForm({ company_name: '', contact_name: '', seller_email: '' })
    load()
  }

  return (
    <div>
      <h3>Sellers CRUD</h3>
      <div style={{ display: 'grid', maxWidth: 300, gap: 6 }}>
        <input value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} placeholder="company_name" />
        <input value={form.contact_name} onChange={(e) => setForm({ ...form, contact_name: e.target.value })} placeholder="contact_name" />
        <input value={form.seller_email} onChange={(e) => setForm({ ...form, seller_email: e.target.value })} placeholder="seller_email" />
        <button onClick={create}>Create Seller</button>
      </div>
      <pre>{JSON.stringify(sellers, null, 2)}</pre>
    </div>
  )
}
