import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function InventoryView() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])
  useEffect(() => { apiRequest('/sellers/inventory', { token }).then(setRows) }, [token])
  return <div><h3>Inventory View</h3><pre>{JSON.stringify(rows, null, 2)}</pre></div>
}
