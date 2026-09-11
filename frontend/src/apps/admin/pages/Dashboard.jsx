import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function Dashboard() {
  const { token } = useAuth()
  const [data, setData] = useState(null)
  useEffect(() => { apiRequest('/admin/dashboard', { token }).then(setData) }, [token])
  return <div><h3>Admin Dashboard</h3><pre>{JSON.stringify(data, null, 2)}</pre></div>
}
