import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const roleLinks = {
  buyer: [
    ['/buyer/events', 'Event Catalog'],
    ['/buyer/register', 'Register'],
    ['/buyer/interview', 'AI Interview'],
    ['/buyer/matches', 'Matches'],
    ['/buyer/consent', 'Consent']
  ],
  operations_admin: [
    ['/admin/dashboard', 'Dashboard'],
    ['/admin/sellers', 'Sellers CRUD'],
    ['/admin/inventory', 'Inventory CRUD'],
    ['/admin/events', 'Events/Sessions'],
    ['/admin/waitlist', 'Waitlist Queue'],
    ['/admin/ai-review', 'AI Review Queue'],
    ['/admin/import', 'CSV Import'],
    ['/admin/weights', 'Matching Weights']
  ],
  super_admin: [
    ['/admin/dashboard', 'Dashboard'],
    ['/admin/sellers', 'Sellers CRUD'],
    ['/admin/inventory', 'Inventory CRUD'],
    ['/admin/events', 'Events/Sessions'],
    ['/admin/waitlist', 'Waitlist Queue'],
    ['/admin/ai-review', 'AI Review Queue'],
    ['/admin/import', 'CSV Import'],
    ['/admin/weights', 'Matching Weights'],
    ['/admin/users', 'Users & Roles']
  ],
  seller: [
    ['/seller/profile', 'Profile'],
    ['/seller/inventory', 'Inventory'],
    ['/seller/leads', 'Leads']
  ]
}

export default function Layout() {
  const { user, role, logout } = useAuth()
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: 16 }}>
      <h2>Real Estate Event Registration</h2>
      <p>
        Logged in as <strong>{user?.email}</strong> ({role}) <button onClick={logout}>Logout</button>
      </p>
      <nav style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 16 }}>
        {(roleLinks[role] || []).map(([to, label]) => (
          <Link key={to} to={to} style={{ border: '1px solid #ccc', padding: 6, borderRadius: 6 }}>
            {label}
          </Link>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
