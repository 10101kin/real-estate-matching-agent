import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function UsersAndRoles() {
  const { token } = useAuth()
  const [users, setUsers] = useState([])
  const load = () => apiRequest('/auth/users', { token }).then(setUsers)
  useEffect(load, [token])

  async function changeRole(id, role) {
    await apiRequest(`/auth/users/${id}/role?role=${role}`, { method: 'PUT', token })
    load()
  }

  return (
    <div>
      <h3>Users & Roles</h3>
      {users.map((u) => (
        <div key={u.id}>{u.email} ({u.role})
          <select onChange={(e) => changeRole(u.id, e.target.value)} defaultValue={u.role}>
            {['buyer', 'seller', 'operations_admin', 'super_admin'].map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      ))}
    </div>
  )
}
