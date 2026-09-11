import { useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function MatchResults() {
  const { token } = useAuth()
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const registrationId = localStorage.getItem('last_registration_id') || ''

  async function run() {
    try {
      setError('')
      const res = await apiRequest(`/matching/run/${registrationId}`, { method: 'POST', token })
      setResults(res)
      if (res[0]) localStorage.setItem('last_match_id', res[0].id)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h3>Match Results</h3>
      <button onClick={run} disabled={!registrationId}>Run Immediate Matching</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {results.map((r) => (
        <div key={r.id} style={{ border: '1px solid #ddd', marginTop: 8, padding: 8 }}>
          <strong>Rank {r.rank}</strong> - Score {r.score}
          <pre>{JSON.stringify(r.breakdown, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}
