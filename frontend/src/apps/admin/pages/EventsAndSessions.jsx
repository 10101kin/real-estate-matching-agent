import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function EventsAndSessions() {
  const { token } = useAuth()
  const [events, setEvents] = useState([])
  const [name, setName] = useState('New Expo')
  const load = () => apiRequest('/events', { token }).then(setEvents)
  useEffect(load, [token])

  async function createEvent() {
    const now = new Date().toISOString()
    await apiRequest('/events', {
      method: 'POST',
      token,
      body: { name, description: 'Created from admin UI', capacity: 100, registration_open_at: now, registration_close_at: now }
    })
    load()
  }

  async function addSession(eventId) {
    const start = new Date(Date.now() + 3600 * 1000).toISOString()
    const end = new Date(Date.now() + 7200 * 1000).toISOString()
    await apiRequest(`/events/${eventId}/sessions`, { method: 'POST', token, body: { title: 'New Session', start_time: start, end_time: end, capacity: 50 } })
    load()
  }

  return (
    <div>
      <h3>Events & Sessions</h3>
      <input value={name} onChange={(e) => setName(e.target.value)} /> <button onClick={createEvent}>Create Event</button>
      {events.map((e) => (
        <div key={e.id} style={{ border: '1px solid #ddd', marginTop: 8, padding: 8 }}>
          <strong>{e.name}</strong> <button onClick={() => addSession(e.id)}>Add Session</button>
          <ul>{e.sessions.map((s) => <li key={s.id}>{s.title}</li>)}</ul>
        </div>
      ))}
    </div>
  )
}
