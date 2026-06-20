import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, AlertTriangle, Search, Users, Shield } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/alerts', label: 'Alerts', icon: AlertTriangle },
  { path: '/transactions', label: 'Transactions', icon: Search },
  { path: '/users', label: 'User Profiles', icon: Users },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Shield className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-lg font-bold">FraudGuard</h1>
            <p className="text-xs text-gray-400">Detection Platform</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        v0.1.0 - Phase 1 MVP
      </div>
    </aside>
  )
}
