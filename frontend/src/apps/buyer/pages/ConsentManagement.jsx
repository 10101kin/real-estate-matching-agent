import { useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function ConsentManagement() {
  const { token } = useAuth()
  const [message, setMessage] = useState('')

  async function consentPerMatch() {
    const matchId = localStorage.getItem('last_match_id')
    const res = await apiRequest('/consents', { method: 'POST', token, body: { consent_scope: 'per_match', match_result_id: matchId } })
    setMessage(`Consent saved: ${res.id}`)
  }

  async function consentPerEvent() {
    const eventId = localStorage.getItem('last_event_id')
    const res = await apiRequest('/consents', { method: 'POST', token, body: { consent_scope: 'per_event', event_id: eventId } })
    setMessage(`Event consent saved: ${res.id}`)
  }

  return (
    <div>
      <h3>Consent Management</h3>
      <button onClick={consentPerMatch}>Consent Per Match</button>{' '}
      <button onClick={consentPerEvent}>Consent Per Event</button>
      {message && <p>{message}</p>}
    </div>
  )
}
