import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function AIInterview() {
  const { token } = useAuth()
  const [form, setForm] = useState({ location: 'Austin', budget_min: 250000, budget_max: 450000, property_type: 'condo', timeframe: '3_months' })
  const [output, setOutput] = useState(null)
  const registrationId = localStorage.getItem('last_registration_id') || ''

  useEffect(() => {
    if (!registrationId) return
    apiRequest(`/buyers/interview/${registrationId}`, { token }).then((d) => setForm(d.answers)).catch(() => {})
  }, [token, registrationId])

  async function save() {
    const res = await apiRequest('/buyers/interview', { method: 'POST', token, body: { registration_id: registrationId, answers: form } })
    setOutput(res)
  }

  return (
    <div>
      <h3>AI Interview (dynamic normalized capture)</h3>
      {!registrationId && <p>Create a registration first.</p>}
      <div style={{ display: 'grid', gap: 6, maxWidth: 360 }}>
        {['location', 'budget_min', 'budget_max', 'property_type', 'timeframe'].map((k) => (
          <input key={k} value={form[k] ?? ''} onChange={(e) => setForm({ ...form, [k]: e.target.value })} placeholder={k} />
        ))}
      </div>
      <button onClick={save} disabled={!registrationId}>Save / Normalize</button>
      {output && <pre>{JSON.stringify(output, null, 2)}</pre>}
    </div>
  )
}
