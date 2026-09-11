import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function EventRegistration() {
  const { token } = useAuth()
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState('')
  const [sessionIds, setSessionIds] = useState([])
  const [message, setMessage] = useState('')

  useEffect(() => {
    apiRequest('/events', { token }).then((data) => {
      setEvents(data)
      if (data[0]) setSelectedEvent(data[0].id)
    })
  }, [token])

  const event = events.find((e) => e.id === selectedEvent)

  async function submit() {
    try {
      const res = await apiRequest('/registrations', { method: 'POST', token, body: { event_id: selectedEvent, session_ids: sessionIds } })
      localStorage.setItem('last_registration_id', res.registration_id)
      localStorage.setItem('last_event_id', selectedEvent)
      setMessage(`Registered with status: ${res.status}. Registration id saved for interview.`)
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <div>
      <h3>Event Registration</h3>
      <select value={selectedEvent} onChange={(e) => { setSelectedEvent(e.target.value); setSessionIds([]) }}>
        {events.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
      </select>
      <div>
        {event?.sessions.map((s) => (
          <label key={s.id} style={{ display: 'block' }}>
            <input type="checkbox" checked={sessionIds.includes(s.id)} onChange={(e) => setSessionIds((prev) => e.target.checked ? [...prev, s.id] : prev.filter((id) => id !== s.id))} />
            {s.title}
          </label>
        ))}
      </div>
      <button onClick={submit}>Submit Registration</button>
      {message && <p>{message}</p>}
    </div>
  )
}
