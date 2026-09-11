import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function MatchingWeights() {
  const { token } = useAuth()
  const [weights, setWeights] = useState({ location: 0.4, budget: 0.3, property_type: 0.2, timeframe: 0.1 })
  useEffect(() => { apiRequest('/matching/weights/current', { token }).then(setWeights) }, [token])
  async function save() {
    const updated = await apiRequest('/matching/weights/current', { method: 'PUT', token, body: weights })
    setWeights(updated)
  }
  return (
    <div>
      <h3>Matching Weights</h3>
      {Object.keys(weights).map((k) => (
        <div key={k}><label>{k}</label><input value={weights[k]} onChange={(e) => setWeights({ ...weights, [k]: Number(e.target.value) })} /></div>
      ))}
      <button onClick={save}>Save Weights</button>
    </div>
  )
}
