import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function LeadsView() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])
  useEffect(() => { apiRequest('/sellers/leads', { token }).then(setRows) }, [token])
  return <div><h3>Consented Leads (read-only)</h3><pre>{JSON.stringify(rows, null, 2)}</pre></div>
}
