import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function InventoryCRUD() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])
  const [sellers, setSellers] = useState([])
  const [form, setForm] = useState({ seller_id: '', external_id: '', location: '', property_type: '', price_min: 0, price_max: 0, metadata_json: {} })

  const load = () => apiRequest('/inventory', { token }).then(setRows)
  useEffect(() => {
    load()
    apiRequest('/admin/sellers', { token }).then((s) => {
      setSellers(s)
      if (s[0]) setForm((f) => ({ ...f, seller_id: s[0].id }))
    })
  }, [token])

  async function create() {
    await apiRequest('/inventory', { method: 'POST', token, body: form })
    load()
  }

  return (
    <div>
      <h3>Inventory CRUD</h3>
      <select value={form.seller_id} onChange={(e) => setForm({ ...form, seller_id: e.target.value })}>
        {sellers.map((s) => <option key={s.id} value={s.id}>{s.company_name}</option>)}
      </select>
      {['external_id', 'location', 'property_type', 'price_min', 'price_max'].map((k) => (
        <input key={k} value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} placeholder={k} />
      ))}
      <button onClick={create}>Create Listing</button>
      <pre>{JSON.stringify(rows, null, 2)}</pre>
    </div>
  )
}
