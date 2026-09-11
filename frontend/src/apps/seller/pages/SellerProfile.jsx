import { useEffect, useState } from 'react'
import { apiRequest } from '../../../services/apiClient'
import { useAuth } from '../../../auth/AuthContext'

export default function SellerProfile() {
  const { token } = useAuth()
  const [profile, setProfile] = useState(null)
  useEffect(() => { apiRequest('/sellers/me', { token }).then(setProfile) }, [token])
  return <div><h3>Seller Profile</h3><pre>{JSON.stringify(profile, null, 2)}</pre></div>
}
