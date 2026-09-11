import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function EventCatalog() {
  const { token } = useAuth()
  const [events, setEvents] = useState([])

  useEffect(() => {
    apiRequest('/events', { token }).then(setEvents)
  }, [token])

  return (
    <div>
      <h3>Event Catalog</h3>
      {events.map((e) => (
        <div key={e.id} style={{ border: '1px solid #ddd', marginBottom: 8, padding: 8 }}>
          <strong>{e.name}</strong> (capacity {e.capacity})
          <div>{e.description}</div>
          <ul>
            {e.sessions.map((s) => (
              <li key={s.id}>{s.title} ({new Date(s.start_time).toLocaleString()} - {new Date(s.end_time).toLocaleTimeString()})</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
