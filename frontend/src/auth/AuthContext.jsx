import { createContext, useContext, useEffect, useState } from 'react'
import { apiRequest, login as loginCall } from '../services/apiClient'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [role, setRole] = useState(localStorage.getItem('role'))
  const [user, setUser] = useState(null)

  useEffect(() => {
    if (!token) return
    apiRequest('/auth/me', { token })
      .then(setUser)
      .catch(() => logout())
  }, [token])

  async function login(email, password) {
    const data = await loginCall(email, password)
    setToken(data.access_token)
    setRole(data.role)
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    const me = await apiRequest('/auth/me', { token: data.access_token })
    setUser(me)
  }

  function logout() {
    setToken(null)
    setRole(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  return <AuthContext.Provider value={{ token, role, user, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
