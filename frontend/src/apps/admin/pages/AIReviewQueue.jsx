import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function AIReviewQueue() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])
  useEffect(() => { apiRequest('/admin/ai-review-queue', { token }).then(setRows) }, [token])
  return <div><h3>AI Review Queue</h3><pre>{JSON.stringify(rows, null, 2)}</pre></div>
}
