import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function WaitlistQueue() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])
  const load = () => apiRequest('/admin/waitlist', { token }).then(setRows)
  useEffect(load, [token])

  async function promote(id) {
    await apiRequest(`/registrations/waitlist/${id}/promote`, { method: 'POST', token })
    load()
  }

  return (
    <div>
      <h3>Waitlist Queue</h3>
      {rows.map((r) => (
        <div key={r.id}>{r.id} pos={r.position} status={r.status} {r.status === 'waiting' && <button onClick={() => promote(r.id)}>Promote</button>}</div>
      ))}
    </div>
  )
}
