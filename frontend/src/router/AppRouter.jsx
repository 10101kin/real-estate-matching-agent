import { Navigate, Route, Routes } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import ProtectedRoute from '../components/ProtectedRoute'
import Layout from '../components/Layout'
import EventCatalog from '../apps/buyer/pages/EventCatalog'
import EventRegistration from '../apps/buyer/pages/EventRegistration'
import AIInterview from '../apps/buyer/pages/AIInterview'
import MatchResults from '../apps/buyer/pages/MatchResults'
import ConsentManagement from '../apps/buyer/pages/ConsentManagement'
import Dashboard from '../apps/admin/pages/Dashboard'
import SellersCRUD from '../apps/admin/pages/SellersCRUD'
import InventoryCRUD from '../apps/admin/pages/InventoryCRUD'
import EventsAndSessions from '../apps/admin/pages/EventsAndSessions'
import WaitlistQueue from '../apps/admin/pages/WaitlistQueue'
import AIReviewQueue from '../apps/admin/pages/AIReviewQueue'
import CSVImport from '../apps/admin/pages/CSVImport'
import MatchingWeights from '../apps/admin/pages/MatchingWeights'
import UsersAndRoles from '../apps/admin/pages/UsersAndRoles'
import SellerProfile from '../apps/seller/pages/SellerProfile'
import InventoryView from '../apps/seller/pages/InventoryView'
import LeadsView from '../apps/seller/pages/LeadsView'

function LoginPage() {
  const { login, token } = useAuth()
  const [email, setEmail] = useState('buyer@example.com')
  const [password, setPassword] = useState('Password123')
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    try {
      setError('')
      await login(email, password)
    } catch (err) {
      setError(err.message)
    }
  }

  if (token) return <Navigate to="/" replace />

  return (
    <div style={{ padding: 16, fontFamily: 'Arial' }}>
      <h2>Login</h2>
      <p>Seed users: buyer@example.com, seller@example.com, opsadmin@example.com, superadmin@example.com (Password123)</p>
      <form onSubmit={submit} style={{ display: 'grid', maxWidth: 320, gap: 10 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
        <button type="submit">Login</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </form>
    </div>
  )
}

export default function AppRouter() {
  const { role } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to={role === 'buyer' ? '/buyer/events' : role === 'seller' ? '/seller/profile' : '/admin/dashboard'} />} />

        <Route path="buyer/events" element={<ProtectedRoute roles={['buyer']}><EventCatalog /></ProtectedRoute>} />
        <Route path="buyer/register" element={<ProtectedRoute roles={['buyer']}><EventRegistration /></ProtectedRoute>} />
        <Route path="buyer/interview" element={<ProtectedRoute roles={['buyer']}><AIInterview /></ProtectedRoute>} />
        <Route path="buyer/matches" element={<ProtectedRoute roles={['buyer']}><MatchResults /></ProtectedRoute>} />
        <Route path="buyer/consent" element={<ProtectedRoute roles={['buyer']}><ConsentManagement /></ProtectedRoute>} />

        <Route path="admin/dashboard" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><Dashboard /></ProtectedRoute>} />
        <Route path="admin/sellers" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><SellersCRUD /></ProtectedRoute>} />
        <Route path="admin/inventory" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><InventoryCRUD /></ProtectedRoute>} />
        <Route path="admin/events" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><EventsAndSessions /></ProtectedRoute>} />
        <Route path="admin/waitlist" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><WaitlistQueue /></ProtectedRoute>} />
        <Route path="admin/ai-review" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><AIReviewQueue /></ProtectedRoute>} />
        <Route path="admin/import" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><CSVImport /></ProtectedRoute>} />
        <Route path="admin/weights" element={<ProtectedRoute roles={['operations_admin', 'super_admin']}><MatchingWeights /></ProtectedRoute>} />
        <Route path="admin/users" element={<ProtectedRoute roles={['super_admin']}><UsersAndRoles /></ProtectedRoute>} />

        <Route path="seller/profile" element={<ProtectedRoute roles={['seller']}><SellerProfile /></ProtectedRoute>} />
        <Route path="seller/inventory" element={<ProtectedRoute roles={['seller']}><InventoryView /></ProtectedRoute>} />
        <Route path="seller/leads" element={<ProtectedRoute roles={['seller']}><LeadsView /></ProtectedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
